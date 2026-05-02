# Guía de Deploy — HAFESA en DigitalOcean

**Droplet**: `146.190.255.117` · Ubuntu 24.04 · Usuario app: `hafesa`  
**Repo**: `https://github.com/tukudecristal-ctrl/HAFESA`  
**Service**: `hafesa` (SystemD)

---

## PASO 0 — Verificar acceso SSH

Antes de todo, confirmar que puedes entrar al droplet:

```bash
ssh root@146.190.255.117
```

**Si pide contraseña**: La definiste al crear el droplet en DigitalOcean.  
**Si dice "Permission denied"**: Revisa en el panel de DO → Droplet → Access → Reset Root Password.  
**Si no tienes llave SSH registrada**: En DO → Settings → Security → SSH Keys, agrega tu llave pública.

Para ver tu llave pública local:
```bash
cat ~/.ssh/id_rsa.pub
# o si usas ed25519:
cat ~/.ssh/id_ed25519.pub
```

---

## PASO 1 — Configuración inicial del servidor

Conectado como root, ejecutar todo esto:

```bash
# Actualizar sistema
apt update && apt upgrade -y

# Instalar dependencias del sistema
apt install -y git nginx postgresql postgresql-contrib \
    build-essential libpq-dev python3-pip python3-venv \
    python3-dev curl wget

# Instalar pyenv para manejar Python 3.13.2
curl https://pyenv.run | bash

# Agregar pyenv al PATH (para root y para el usuario hafesa que crearemos)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

# Instalar Python 3.13.2
pyenv install 3.13.2
pyenv global 3.13.2
python3 --version   # debe mostrar 3.13.2
```

---

## PASO 2 — Crear usuario hafesa

```bash
# Crear usuario del sistema (sin shell interactivo para el servicio)
adduser --disabled-password --gecos "" hafesa

# Crear directorio de la app
mkdir -p /home/hafesa/app
chown -R hafesa:hafesa /home/hafesa/app

# Agregar pyenv al perfil de hafesa
echo 'export PYENV_ROOT="/root/.pyenv"' >> /home/hafesa/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> /home/hafesa/.bashrc
echo 'eval "$(pyenv init -)"' >> /home/hafesa/.bashrc
```

---

## PASO 3 — Configurar PostgreSQL

```bash
# Iniciar y habilitar PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Crear usuario y base de datos
sudo -u postgres psql << 'EOF'
CREATE USER admin_verde WITH PASSWORD 'HaFeSa@2026';
CREATE DATABASE verde OWNER admin_verde;
GRANT ALL PRIVILEGES ON DATABASE verde TO admin_verde;
\q
EOF
```

---

## PASO 4 — Restaurar el backup de la base de datos

Desde tu máquina local, copiar el backup al servidor:

```bash
# Ejecutar en tu máquina local (no en el servidor)
scp /Users/darh/proyectos/VERDE/verde_backup_20260427.sql root@146.190.255.117:/tmp/
```

Luego en el servidor:

```bash
# Restaurar la BD
sudo -u postgres psql -d verde -f /tmp/verde_backup_20260427.sql

# Verificar que las tablas existen
sudo -u postgres psql -d verde -c "\dt"

# Limpiar el archivo temporal
rm /tmp/verde_backup_20260427.sql
```

---

## PASO 5 — Clonar el repositorio y configurar la app

```bash
# Cambiar al usuario hafesa
su - hafesa

# Configurar git (para que el CI/CD de GitHub pueda hacer pull)
cd /home/hafesa/app
git clone https://github.com/tukudecristal-ctrl/HAFESA .

# Crear entorno virtual Python
/root/.pyenv/versions/3.13.2/bin/python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r backend/requirements.txt

# Verificar que el backend arranca (prueba rápida)
cd backend
uvicorn main:app --host 127.0.0.1 --port 8000 &
sleep 3
curl -s http://127.0.0.1:8000/ | head -5
kill %1
cd ..

# Salir del usuario hafesa
exit
```

---

## PASO 6 — Crear el archivo .env de producción

```bash
# Como root, crear el .env con variables de producción
cat > /home/hafesa/app/backend/.env << 'EOF'
DATABASE_URL=postgresql://admin_verde:HaFeSa%402026@localhost:5432/verde
SECRET_KEY=CAMBIA_ESTO_POR_UNA_CLAVE_LARGA_Y_ALEATORIA
EOF

# Asegurar permisos correctos (solo hafesa puede leerlo)
chown hafesa:hafesa /home/hafesa/app/backend/.env
chmod 600 /home/hafesa/app/backend/.env
```

> **IMPORTANTE**: Genera una `SECRET_KEY` segura con:
> ```bash
> python3 -c "import secrets; print(secrets.token_hex(32))"
> ```
> Reemplaza `CAMBIA_ESTO_POR_UNA_CLAVE_LARGA_Y_ALEATORIA` con el resultado.

---

## PASO 7 — Crear el servicio SystemD

```bash
cat > /etc/systemd/system/hafesa.service << 'EOF'
[Unit]
Description=HAFESA - Sistema de Ventas
After=network.target postgresql.service

[Service]
User=hafesa
Group=hafesa
WorkingDirectory=/home/hafesa/app/backend
ExecStart=/home/hafesa/app/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
Environment="PATH=/home/hafesa/app/venv/bin"

[Install]
WantedBy=multi-user.target
EOF

# Habilitar e iniciar el servicio
systemctl daemon-reload
systemctl enable hafesa
systemctl start hafesa

# Verificar que está corriendo
systemctl status hafesa
```

---

## PASO 8 — Configurar Nginx como reverse proxy

```bash
cat > /etc/nginx/sites-available/hafesa << 'EOF'
server {
    listen 80;
    server_name 146.190.255.117;

    # Aumentar límite para subida de imágenes
    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 60s;
    }
}
EOF

# Activar el sitio
ln -s /etc/nginx/sites-available/hafesa /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Verificar configuración y reiniciar
nginx -t
systemctl restart nginx
systemctl enable nginx
```

---

## PASO 9 — Configurar GitHub Actions (CI/CD automático)

En tu máquina local, generar un par de llaves SSH dedicado para el deploy:

```bash
# En tu máquina local
ssh-keygen -t ed25519 -C "hafesa-deploy" -f ~/.ssh/hafesa_deploy -N ""
```

En el servidor, autorizar esa llave:

```bash
# En el servidor como root
mkdir -p /home/hafesa/.ssh
# Pega aquí el contenido de ~/.ssh/hafesa_deploy.pub (de tu máquina local)
echo "PEGA_AQUI_EL_CONTENIDO_DE_hafesa_deploy.pub" >> /home/hafesa/.ssh/authorized_keys
chown -R hafesa:hafesa /home/hafesa/.ssh
chmod 700 /home/hafesa/.ssh
chmod 600 /home/hafesa/.ssh/authorized_keys

# Dar permisos a hafesa para reiniciar el servicio sin sudo
echo "hafesa ALL=(ALL) NOPASSWD: /bin/systemctl restart hafesa" >> /etc/sudoers.d/hafesa
```

En GitHub → repo HAFESA → Settings → Secrets and variables → Actions, crear:

| Secret | Valor |
|--------|-------|
| `DO_HOST` | `146.190.255.117` |
| `DO_USER` | `hafesa` |
| `DO_SSH_KEY` | Contenido completo de `~/.ssh/hafesa_deploy` (llave **privada**) |

Verificar que el workflow funciona:

```bash
# En tu máquina local, hacer un commit y push
git add .
git commit -m "test: verificar CI/CD"
git push origin main
```

Luego ir a GitHub → Actions y ver si el deploy pasa verde.

---

## PASO 10 — Verificación final

```bash
# Desde tu máquina local
curl http://146.190.255.117/
# Debe redirigir / responder con el login

curl http://146.190.255.117/api/auth/login \
  -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"tu_password"}'
```

Desde el navegador: `http://146.190.255.117` → debe cargar el login de HAFESA.

---

## Comandos útiles post-deploy

```bash
# Ver logs del servicio en tiempo real
journalctl -u hafesa -f

# Reiniciar la app manualmente
systemctl restart hafesa

# Ver estado
systemctl status hafesa

# Reiniciar Nginx
systemctl restart nginx

# Hacer backup de la BD
sudo -u postgres pg_dump verde > /home/hafesa/backups/verde_$(date +%Y%m%d).sql
```

---

## Resumen de puertos y rutas

| Componente | Dirección |
|---|---|
| Nginx (público) | `0.0.0.0:80` |
| Uvicorn (interno) | `127.0.0.1:8000` |
| PostgreSQL (interno) | `127.0.0.1:5432` |
| App (browser) | `http://146.190.255.117` |
| API docs | `http://146.190.255.117/docs` |
