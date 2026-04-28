--
-- PostgreSQL database dump
--

\restrict 3RAQHn7VHfkyfcOAlrRqsnzVXpOZ38U8a77XTaLHbxKkeRaIlfgLUy2MJcuG3LC

-- Dumped from database version 16.13 (Ubuntu 16.13-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.13 (Ubuntu 16.13-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agencias_destino; Type: TABLE; Schema: public; Owner: admin_verde
--

CREATE TABLE public.agencias_destino (
    id integer NOT NULL,
    ciudad character varying(100) NOT NULL,
    direccion character varying(200),
    activo boolean DEFAULT true
);


ALTER TABLE public.agencias_destino OWNER TO admin_verde;

--
-- Name: agencias_destino_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_verde
--

CREATE SEQUENCE public.agencias_destino_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.agencias_destino_id_seq OWNER TO admin_verde;

--
-- Name: agencias_destino_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_verde
--

ALTER SEQUENCE public.agencias_destino_id_seq OWNED BY public.agencias_destino.id;


--
-- Name: compras; Type: TABLE; Schema: public; Owner: admin_verde
--

CREATE TABLE public.compras (
    id integer NOT NULL,
    empresa_id integer,
    proveedor character varying(150),
    fecha_compra date NOT NULL,
    costo_transporte numeric(10,2) DEFAULT 0,
    costo_impuesto numeric(10,2) DEFAULT 0,
    otros_costos numeric(10,2) DEFAULT 0,
    total_calculado numeric(10,2),
    observaciones text,
    created_at timestamp without time zone DEFAULT now(),
    proveedor_id integer
);


ALTER TABLE public.compras OWNER TO admin_verde;

--
-- Name: compras_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_verde
--

CREATE SEQUENCE public.compras_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.compras_id_seq OWNER TO admin_verde;

--
-- Name: compras_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_verde
--

ALTER SEQUENCE public.compras_id_seq OWNED BY public.compras.id;


--
-- Name: detalle_compra; Type: TABLE; Schema: public; Owner: admin_verde
--

CREATE TABLE public.detalle_compra (
    id integer NOT NULL,
    compra_id integer,
    producto_id integer,
    cantidad integer NOT NULL,
    costo_unitario numeric(10,2) NOT NULL,
    subtotal numeric(10,2) GENERATED ALWAYS AS (((cantidad)::numeric * costo_unitario)) STORED
);


ALTER TABLE public.detalle_compra OWNER TO admin_verde;

--
-- Name: detalle_compra_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_verde
--

CREATE SEQUENCE public.detalle_compra_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.detalle_compra_id_seq OWNER TO admin_verde;

--
-- Name: detalle_compra_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_verde
--

ALTER SEQUENCE public.detalle_compra_id_seq OWNED BY public.detalle_compra.id;


--
-- Name: detalle_pedido; Type: TABLE; Schema: public; Owner: admin_verde
--

CREATE TABLE public.detalle_pedido (
    id integer NOT NULL,
    pedido_id integer NOT NULL,
    producto_id integer NOT NULL,
    cantidad integer NOT NULL,
    precio_unitario numeric(10,2) NOT NULL,
    subtotal numeric(10,2) GENERATED ALWAYS AS (((cantidad)::numeric * precio_unitario)) STORED,
    CONSTRAINT detalle_pedido_cantidad_check CHECK ((cantidad > 0))
);


ALTER TABLE public.detalle_pedido OWNER TO admin_verde;

--
-- Name: detalle_pedido_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_verde
--

CREATE SEQUENCE public.detalle_pedido_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.detalle_pedido_id_seq OWNER TO admin_verde;

--
-- Name: detalle_pedido_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_verde
--

ALTER SEQUENCE public.detalle_pedido_id_seq OWNED BY public.detalle_pedido.id;


--
-- Name: empresas; Type: TABLE; Schema: public; Owner: admin_verde
--

CREATE TABLE public.empresas (
    id integer NOT NULL,
    codigo character varying(10) NOT NULL,
    nombre character varying(100) NOT NULL,
    rubro character varying(50),
    activo boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now(),
    porcentaje_comision numeric(5,2) DEFAULT 3.00
);


ALTER TABLE public.empresas OWNER TO admin_verde;

--
-- Name: empresas_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_verde
--

CREATE SEQUENCE public.empresas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.empresas_id_seq OWNER TO admin_verde;

--
-- Name: empresas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_verde
--

ALTER SEQUENCE public.empresas_id_seq OWNED BY public.empresas.id;


--
-- Name: flujo_log; Type: TABLE; Schema: public; Owner: admin_verde
--

CREATE TABLE public.flujo_log (
    id integer NOT NULL,
    pedido_id integer,
    estado_anterior character varying(30),
    estado_nuevo character varying(30),
    usuario character varying(100),
    observacion text,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.flujo_log OWNER TO admin_verde;

--
-- Name: flujo_log_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_verde
--

CREATE SEQUENCE public.flujo_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.flujo_log_id_seq OWNER TO admin_verde;

--
-- Name: flujo_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_verde
--

ALTER SEQUENCE public.flujo_log_id_seq OWNED BY public.flujo_log.id;


--
-- Name: pedidos; Type: TABLE; Schema: public; Owner: admin_verde
--

CREATE TABLE public.pedidos (
    id integer NOT NULL,
    empresa_id integer,
    vendedor_id integer,
    nombre_cliente character varying(200) NOT NULL,
    dni character varying(10) NOT NULL,
    telefono character varying(9) NOT NULL,
    producto_id integer,
    cantidad integer,
    agencia_id integer,
    detalle_observacion text,
    separacion numeric(10,2) DEFAULT 0,
    costo_envio numeric(10,2) DEFAULT 0,
    precio_total numeric(10,2),
    resta_pagar numeric(10,2),
    estado character varying(30) DEFAULT 'REGISTRADO'::character varying,
    fecha_registro timestamp without time zone DEFAULT now(),
    fecha_empacado timestamp without time zone,
    fecha_rotulo timestamp without time zone,
    fecha_deposito timestamp without time zone,
    fecha_entrega timestamp without time zone,
    fecha_cancelado timestamp without time zone,
    descuento numeric(10,2) DEFAULT 0,
    fecha_pago_comision timestamp without time zone,
    CONSTRAINT pedidos_dni_check CHECK (((length((dni)::text) >= 8) AND ((dni)::text ~ '^\d{8,10}$'::text))),
    CONSTRAINT pedidos_telefono_check CHECK (((telefono)::text ~ '^9\d{8}$'::text))
);


ALTER TABLE public.pedidos OWNER TO admin_verde;

--
-- Name: pedidos_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_verde
--

CREATE SEQUENCE public.pedidos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pedidos_id_seq OWNER TO admin_verde;

--
-- Name: pedidos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_verde
--

ALTER SEQUENCE public.pedidos_id_seq OWNED BY public.pedidos.id;


--
-- Name: productos; Type: TABLE; Schema: public; Owner: admin_verde
--

CREATE TABLE public.productos (
    id integer NOT NULL,
    codigo character varying(30) NOT NULL,
    nombre character varying(200) NOT NULL,
    descripcion text,
    empresa_id integer,
    precio_venta numeric(10,2) NOT NULL,
    stock integer DEFAULT 0,
    activo boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now(),
    precio_venta_1 numeric(10,2) DEFAULT 0,
    precio_venta_2 numeric(10,2) DEFAULT 0,
    precio_venta_3 numeric(10,2) DEFAULT 0,
    porcentaje_comision numeric(5,2) DEFAULT 3.00,
    stock_comprometido integer DEFAULT 0,
    imagen_url character varying(255)
);


ALTER TABLE public.productos OWNER TO admin_verde;

--
-- Name: productos_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_verde
--

CREATE SEQUENCE public.productos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.productos_id_seq OWNER TO admin_verde;

--
-- Name: productos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_verde
--

ALTER SEQUENCE public.productos_id_seq OWNED BY public.productos.id;


--
-- Name: proveedores; Type: TABLE; Schema: public; Owner: admin_verde
--

CREATE TABLE public.proveedores (
    id integer NOT NULL,
    codigo character varying(20) NOT NULL,
    nombre character varying(150) NOT NULL,
    contacto character varying(100),
    telefono character varying(20),
    activo boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.proveedores OWNER TO admin_verde;

--
-- Name: proveedores_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_verde
--

CREATE SEQUENCE public.proveedores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.proveedores_id_seq OWNER TO admin_verde;

--
-- Name: proveedores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_verde
--

ALTER SEQUENCE public.proveedores_id_seq OWNED BY public.proveedores.id;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: admin_verde
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    dni character varying(8) NOT NULL,
    password_hash character varying(255) NOT NULL,
    nombre character varying(150) NOT NULL,
    rol character varying(20) NOT NULL,
    vendedor_id integer,
    activo boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now(),
    CONSTRAINT usuarios_rol_check CHECK (((rol)::text = ANY ((ARRAY['administrador'::character varying, 'vendedor'::character varying, 'logistica'::character varying])::text[])))
);


ALTER TABLE public.usuarios OWNER TO admin_verde;

--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_verde
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuarios_id_seq OWNER TO admin_verde;

--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_verde
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- Name: vendedores; Type: TABLE; Schema: public; Owner: admin_verde
--

CREATE TABLE public.vendedores (
    id integer NOT NULL,
    codigo character varying(20) NOT NULL,
    nombre_completo character varying(150) NOT NULL,
    empresa_id integer,
    telefono character varying(9),
    activo boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.vendedores OWNER TO admin_verde;

--
-- Name: vendedores_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_verde
--

CREATE SEQUENCE public.vendedores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vendedores_id_seq OWNER TO admin_verde;

--
-- Name: vendedores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_verde
--

ALTER SEQUENCE public.vendedores_id_seq OWNED BY public.vendedores.id;


--
-- Name: agencias_destino id; Type: DEFAULT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.agencias_destino ALTER COLUMN id SET DEFAULT nextval('public.agencias_destino_id_seq'::regclass);


--
-- Name: compras id; Type: DEFAULT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.compras ALTER COLUMN id SET DEFAULT nextval('public.compras_id_seq'::regclass);


--
-- Name: detalle_compra id; Type: DEFAULT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.detalle_compra ALTER COLUMN id SET DEFAULT nextval('public.detalle_compra_id_seq'::regclass);


--
-- Name: detalle_pedido id; Type: DEFAULT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.detalle_pedido ALTER COLUMN id SET DEFAULT nextval('public.detalle_pedido_id_seq'::regclass);


--
-- Name: empresas id; Type: DEFAULT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.empresas ALTER COLUMN id SET DEFAULT nextval('public.empresas_id_seq'::regclass);


--
-- Name: flujo_log id; Type: DEFAULT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.flujo_log ALTER COLUMN id SET DEFAULT nextval('public.flujo_log_id_seq'::regclass);


--
-- Name: pedidos id; Type: DEFAULT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.pedidos ALTER COLUMN id SET DEFAULT nextval('public.pedidos_id_seq'::regclass);


--
-- Name: productos id; Type: DEFAULT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.productos ALTER COLUMN id SET DEFAULT nextval('public.productos_id_seq'::regclass);


--
-- Name: proveedores id; Type: DEFAULT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.proveedores ALTER COLUMN id SET DEFAULT nextval('public.proveedores_id_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- Name: vendedores id; Type: DEFAULT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.vendedores ALTER COLUMN id SET DEFAULT nextval('public.vendedores_id_seq'::regclass);


--
-- Data for Name: agencias_destino; Type: TABLE DATA; Schema: public; Owner: admin_verde
--

COPY public.agencias_destino (id, ciudad, direccion, activo) FROM stdin;
1	Lima - Central	Av. México 333, La Victoria	t
2	Arequipa	Av. Goyeneche 123, Arequipa	t
3	Cusco	Av. El Sol 456, Cusco	t
4	Trujillo	Jr. Gamarra 200, Trujillo	t
5	Chiclayo	Av. Balta 789, Chiclayo	t
6	Piura	Jr. Loreto 111, Piura	t
7	Iquitos	Av. Quiñones 321, Iquitos	t
8	Huancayo	Av. Ferrocarril 555, Huancayo	t
9	Pucallpa	Jr. Ucayali 88, Pucallpa	t
10	Tacna	Av. Bolognesi 210, Tacna	t
11	Juliaca	Jr. Moquegua 45, Juliaca	t
12	Ayacucho	Jr. Lima 77, Ayacucho	t
13	Puno	Jr. Deustua 90, Puno	t
14	Cajamarca	Av. Hoyos Rubio 60, Cajamarca	t
15	Chimbote	Av. José Pardo 400, Chimbote	t
16	Sullana	Jr. Tarapacá 30, Sullana	t
17	Tumbes	Av. Tumbes Norte 150, Tumbes	t
18	Moyobamba	Jr. San Martín 20, Moyobamba	t
19	Tarapoto	Jr. Ramírez Hurtado 55, Tarapoto	t
20	Huaraz	Jr. Luzuriaga 180, Huaraz	t
\.


--
-- Data for Name: compras; Type: TABLE DATA; Schema: public; Owner: admin_verde
--

COPY public.compras (id, empresa_id, proveedor, fecha_compra, costo_transporte, costo_impuesto, otros_costos, total_calculado, observaciones, created_at, proveedor_id) FROM stdin;
2	1	Proveedor Test	2026-04-13	0.00	0.00	0.00	5000.00	\N	2026-04-13 18:20:17.935108	\N
3	2	\N	2026-04-13	0.00	0.00	0.00	2340.00	\N	2026-04-13 18:55:43.341208	2
4	2	\N	2026-04-13	0.00	0.00	0.00	1944.00	\N	2026-04-13 18:56:49.053923	2
5	2	\N	2026-04-15	0.00	0.00	0.00	799.60	\N	2026-04-14 22:21:50.519226	2
6	1	\N	2026-04-19	0.00	0.00	0.00	15270.00	\N	2026-04-19 09:57:29.848412	1
7	1	\N	2026-04-20	0.00	0.00	0.00	637.00	\N	2026-04-20 16:50:08.508522	\N
\.


--
-- Data for Name: detalle_compra; Type: TABLE DATA; Schema: public; Owner: admin_verde
--

COPY public.detalle_compra (id, compra_id, producto_id, cantidad, costo_unitario) FROM stdin;
1	2	2	10	500.00
2	3	8	10	234.00
3	4	8	8	243.00
4	5	7	1	30.00
5	5	6	11	20.00
6	5	9	12	45.80
7	6	2	11	120.00
8	6	4	31	450.00
9	7	2	91	7.00
\.


--
-- Data for Name: detalle_pedido; Type: TABLE DATA; Schema: public; Owner: admin_verde
--

COPY public.detalle_pedido (id, pedido_id, producto_id, cantidad, precio_unitario) FROM stdin;
1	6	1	1	456.00
2	6	2	4	0.00
3	7	1	3	0.00
4	8	1	1	456.00
5	8	1	3	0.00
6	8	1	7	0.00
7	8	1	13	0.00
8	9	3	1	120.00
9	10	3	3	0.00
10	11	3	7	0.00
11	12	4	1	980.00
12	13	10	2	180.00
13	13	6	1	280.00
14	14	2	4	750.00
15	14	4	1	980.00
16	15	6	3	270.00
17	15	7	1	650.00
18	16	9	1	1450.00
\.


--
-- Data for Name: empresas; Type: TABLE DATA; Schema: public; Owner: admin_verde
--

COPY public.empresas (id, codigo, nombre, rubro, activo, created_at, porcentaje_comision) FROM stdin;
1	EMP001	Verde s.a.c	LUMINARIAS	t	2026-04-13 18:07:16.013069	3.00
2	EMP002	JIUZHU s.a.c	SONIDO	t	2026-04-13 18:07:16.013069	5.30
\.


--
-- Data for Name: flujo_log; Type: TABLE DATA; Schema: public; Owner: admin_verde
--

COPY public.flujo_log (id, pedido_id, estado_anterior, estado_nuevo, usuario, observacion, created_at) FROM stdin;
1	1	REGISTRADO	EMPACADO	backoffice	\N	2026-04-13 18:29:54.224565
2	1	EMPACADO	ROTULO_IMPRESO	backoffice	\N	2026-04-13 18:30:24.544985
3	1	ROTULO_IMPRESO	DEPOSITADO	backoffice	\N	2026-04-13 18:30:28.913004
4	2	REGISTRADO	EMPACADO	backoffice	\N	2026-04-13 19:01:08.830819
5	2	EMPACADO	ROTULO_IMPRESO	backoffice	\N	2026-04-14 09:32:51.380238
6	2	ROTULO_IMPRESO	DEPOSITADO	backoffice	\N	2026-04-14 09:32:56.136636
7	3	REGISTRADO	EMPACADO	backoffice	\N	2026-04-14 22:11:29.467062
8	3	EMPACADO	ROTULO_IMPRESO	backoffice	\N	2026-04-14 22:11:36.781181
9	6	REGISTRADO	EMPACADO	test	\N	2026-04-17 20:03:39.094346
10	6	EMPACADO	ROTULO_IMPRESO	test	\N	2026-04-17 20:03:39.214564
11	6	ROTULO_IMPRESO	DEPOSITADO	test	\N	2026-04-17 20:03:39.336472
12	7	REGISTRADO	CANCELADO	test	\N	2026-04-17 20:04:32.756897
13	12	REGISTRADO	EMPACADO	backoffice	\N	2026-04-17 20:25:11.545909
14	8	REGISTRADO	CANCELADO	backoffice	\N	2026-04-17 20:27:22.910157
15	12	EMPACADO	ROTULO_IMPRESO	backoffice	\N	2026-04-17 21:22:20.246341
16	12	ROTULO_IMPRESO	DEPOSITADO	backoffice	\N	2026-04-17 21:22:24.228409
17	12	DEPOSITADO	ENTREGADO	backoffice	\N	2026-04-17 21:22:29.395088
18	3	ROTULO_IMPRESO	DEPOSITADO	backoffice	\N	2026-04-17 21:22:38.979808
19	6	DEPOSITADO	ENTREGADO	backoffice	\N	2026-04-17 21:22:42.317399
20	3	DEPOSITADO	ENTREGADO	backoffice	\N	2026-04-17 21:22:48.735533
21	2	DEPOSITADO	ENTREGADO	backoffice	\N	2026-04-17 21:22:52.468413
22	1	DEPOSITADO	ENTREGADO	backoffice	\N	2026-04-19 09:48:10.484955
23	13	REGISTRADO	EMPACADO	backoffice	\N	2026-04-19 09:54:45.190363
24	13	EMPACADO	ROTULO_IMPRESO	backoffice	\N	2026-04-19 09:54:47.511034
25	13	ROTULO_IMPRESO	DEPOSITADO	backoffice	\N	2026-04-19 09:54:49.961342
26	13	DEPOSITADO	ENTREGADO	backoffice	\N	2026-04-19 09:57:44.610606
27	14	REGISTRADO	EMPACADO	backoffice	\N	2026-04-20 16:48:08.476556
28	14	EMPACADO	ROTULO_IMPRESO	backoffice	\N	2026-04-20 16:48:10.388375
29	14	ROTULO_IMPRESO	DEPOSITADO	backoffice	\N	2026-04-20 16:48:14.87836
30	14	DEPOSITADO	ENTREGADO	backoffice	\N	2026-04-20 16:50:56.346808
31	11	REGISTRADO	EMPACADO	backoffice	\N	2026-04-20 16:53:29.115316
32	11	EMPACADO	ROTULO_IMPRESO	backoffice	\N	2026-04-20 16:53:32.691887
33	11	ROTULO_IMPRESO	DEPOSITADO	backoffice	\N	2026-04-20 16:53:36.20107
34	5	REGISTRADO	EMPACADO	backoffice	\N	2026-04-20 16:54:18.138939
35	15	REGISTRADO	EMPACADO	backoffice	\N	2026-04-20 16:58:11.413917
36	15	EMPACADO	ROTULO_IMPRESO	backoffice	\N	2026-04-20 16:58:13.012043
37	15	ROTULO_IMPRESO	DEPOSITADO	backoffice	\N	2026-04-20 16:58:18.276894
38	15	DEPOSITADO	ENTREGADO	backoffice	\N	2026-04-20 16:58:22.137849
39	16	REGISTRADO	EMPACADO	backoffice	\N	2026-04-20 17:00:57.02254
40	16	EMPACADO	ROTULO_IMPRESO	backoffice	\N	2026-04-20 17:00:58.250039
41	16	ROTULO_IMPRESO	DEPOSITADO	backoffice	\N	2026-04-20 17:00:59.776297
42	16	DEPOSITADO	ENTREGADO	backoffice	\N	2026-04-20 17:01:01.791581
\.


--
-- Data for Name: pedidos; Type: TABLE DATA; Schema: public; Owner: admin_verde
--

COPY public.pedidos (id, empresa_id, vendedor_id, nombre_cliente, dni, telefono, producto_id, cantidad, agencia_id, detalle_observacion, separacion, costo_envio, precio_total, resta_pagar, estado, fecha_registro, fecha_empacado, fecha_rotulo, fecha_deposito, fecha_entrega, fecha_cancelado, descuento, fecha_pago_comision) FROM stdin;
4	1	2	Raul Juan	9998887776	900087777	3	2	18	toca la puerta	30.00	0.00	240.00	210.00	REGISTRADO	2026-04-14 22:15:39.996602	\N	\N	\N	\N	\N	0.00	\N
7	1	1	Maria Cancelacion	0987654321	912345678	\N	\N	1	\N	0.00	0.00	0.00	0.00	CANCELADO	2026-04-17 20:04:32.613664	\N	\N	\N	\N	2026-04-17 20:04:32.760864	0.00	\N
9	1	1	Test	2222222221	922222222	\N	\N	1	\N	0.00	0.00	120.00	120.00	REGISTRADO	2026-04-17 20:06:24.171993	\N	\N	\N	\N	\N	0.00	\N
10	1	1	Test	2222222223	922222222	\N	\N	1	\N	0.00	0.00	0.00	0.00	REGISTRADO	2026-04-17 20:06:24.317947	\N	\N	\N	\N	\N	0.00	\N
8	1	1	Test Precios	1111111111	911111111	\N	\N	1	\N	0.00	0.00	456.00	456.00	CANCELADO	2026-04-17 20:06:24.063534	\N	\N	\N	\N	2026-04-17 20:27:22.924622	0.00	\N
3	2	5	asasdfsdf	3213123122	987456321	8	3	9	llma a	30.00	0.00	2670.00	2640.00	ENTREGADO	2026-04-14 09:34:28.521972	2026-04-14 22:11:29.518946	2026-04-14 22:11:36.805189	2026-04-17 21:22:38.981995	2026-04-17 21:22:48.739969	\N	0.00	2026-04-18 00:00:00
1	1	1	Juan Prueba	1234567890	987654321	1	2	3	\N	100.00	20.00	920.00	820.00	ENTREGADO	2026-04-13 18:12:35.389874	2026-04-13 18:29:54.226654	2026-04-13 18:30:24.545793	2026-04-13 18:30:28.913785	2026-04-19 09:48:10.516594	\N	0.00	\N
2	1	3	Carle Guzman	9988877760	987676785	2	3	19	Shalom Alfonso Ugarte	250.00	0.00	2250.00	2000.00	ENTREGADO	2026-04-13 18:33:10.859293	2026-04-13 19:01:08.835308	2026-04-14 09:32:51.476596	2026-04-14 09:32:56.143812	2026-04-17 21:22:52.471685	\N	0.00	2026-04-19 00:00:00
12	1	3	JUan Gonzales	98987676	987698766	\N	\N	10	op	30.00	0.00	980.00	850.00	ENTREGADO	2026-04-17 20:23:56.666216	2026-04-17 20:25:11.54833	2026-04-17 21:22:20.252833	2026-04-17 21:22:24.238764	2026-04-17 21:22:29.397613	\N	100.00	2026-04-19 00:00:00
14	1	2	juanito	88888888	999999999	\N	\N	20	kkkj	100.00	0.00	3980.00	3850.00	ENTREGADO	2026-04-20 16:47:25.28784	2026-04-20 16:48:08.479076	2026-04-20 16:48:10.391137	2026-04-20 16:48:14.882682	2026-04-20 16:50:56.349746	\N	30.00	\N
6	1	1	Juan Prueba Lopez	1234567890	987654321	\N	\N	2	\N	100.00	30.00	486.00	366.00	ENTREGADO	2026-04-17 20:03:17.57221	2026-04-17 20:03:39.098108	2026-04-17 20:03:39.215692	2026-04-17 20:03:39.342404	2026-04-17 21:22:42.31918	\N	20.00	2026-04-20 00:00:00
13	2	6	Caleb	234234443	973736464	\N	\N	17	Llamar 30 min antes	30.00	20.00	660.00	630.00	ENTREGADO	2026-04-19 09:52:10.843936	2026-04-19 09:54:45.192334	2026-04-19 09:54:47.513185	2026-04-19 09:54:49.968536	2026-04-19 09:57:44.619978	\N	0.00	2026-04-20 00:00:00
11	1	1	Test	2222222227	922222222	\N	\N	1	\N	0.00	0.00	0.00	0.00	DEPOSITADO	2026-04-17 20:06:24.452363	2026-04-20 16:53:29.116828	2026-04-20 16:53:32.693983	2026-04-20 16:53:36.205669	\N	\N	0.00	\N
5	1	1	oioipo	9999999999	988887777	2	2	19	\N	120.00	0.00	1500.00	1380.00	EMPACADO	2026-04-14 22:31:17.006086	2026-04-20 16:54:18.140866	\N	\N	\N	\N	0.00	\N
15	2	4	Juanito	77777777	987878787	\N	\N	19	\N	0.00	20.00	1480.00	1420.00	ENTREGADO	2026-04-20 16:57:44.721146	2026-04-20 16:58:11.416428	2026-04-20 16:58:13.014941	2026-04-20 16:58:18.285327	2026-04-20 16:58:22.139954	\N	60.00	\N
16	2	4	uyt	88888888	999999999	\N	\N	16	\N	0.00	20.00	1470.00	1470.00	ENTREGADO	2026-04-20 17:00:32.76726	2026-04-20 17:00:57.024061	2026-04-20 17:00:58.251194	2026-04-20 17:00:59.782989	2026-04-20 17:01:01.793587	\N	0.00	\N
\.


--
-- Data for Name: productos; Type: TABLE DATA; Schema: public; Owner: admin_verde
--

COPY public.productos (id, codigo, nombre, descripcion, empresa_id, precio_venta, stock, activo, created_at, precio_venta_1, precio_venta_2, precio_venta_3, porcentaje_comision, stock_comprometido, imagen_url) FROM stdin;
10	AUDIO-MIC-UHF	Micrófono UHF Inalámbrico	Sistema UHF doble micrófono, 80m alcance, anti-interferencia	2	180.00	43	t	2026-04-13 18:07:16.06181	180.00	180.00	180.00	3.00	0	\N
4	LUMI-KIT-DOM	Kit Solar Doméstico	Kit panel 100W + batería 12V 50Ah + controlador	1	980.00	49	t	2026-04-13 18:07:16.057159	980.00	980.00	980.00	3.00	0	\N
2	LUMI-FAR-60W	Farola Solar 60W	Farola solar LED 60W, panel monocristalino, batería LiFePO4	1	750.00	134	t	2026-04-13 18:07:16.057159	750.00	750.00	750.00	3.00	0	\N
3	LUMI-LAMP-10W	Lámpara Solar 10W	Lámpara solar portátil 10W, carga USB, 8h autonomía	1	120.00	93	t	2026-04-13 18:07:16.057159	120.00	120.00	120.00	3.00	4	\N
6	AUDIO-PARL-8P	Parlante 8" Portátil	Parlante Bluetooth 8 pulgadas, 80W RMS, batería 6h	2	280.00	67	t	2026-04-13 18:07:16.06181	270.00	260.00	250.00	3.00	0	\N
7	AUDIO-PARL-15P	Parlante 15" Torre	Parlante torre 15 pulgadas, 300W RMS, karaoke, TWS	2	650.00	25	t	2026-04-13 18:07:16.06181	650.00	650.00	650.00	3.00	0	\N
9	AUDIO-VG-4MP	Videograbadora 4MP	Kit NVR 8 cámaras 4MP IP, disco 2TB, acceso remoto	2	1450.00	21	t	2026-04-13 18:07:16.06181	1450.00	1450.00	1450.00	3.00	0	\N
5	LUMI-PANEL-200W	Panel Solar 200W	Panel policristalino 200W, 24V, garantía 25 años	1	320.00	40	t	2026-04-13 18:07:16.057159	320.00	320.00	320.00	3.00	0	\N
8	AUDIO-VG-2MP	Videograbadora 2MP	Kit DVR 4 cámaras 2MP, disco 1TB, visión nocturna	2	890.00	33	t	2026-04-13 18:07:16.06181	890.00	890.00	890.00	3.00	0	\N
11	TEST-REP	Producto Replica	\N	1	250.00	0	t	2026-04-17 20:10:29.44092	250.00	250.00	250.00	3.00	0	\N
1	LUMI-FAR-30W	Farola Solar 30W	Farola solar LED 30W, panel monocristalino, batería LiFePO4	1	456.00	49	t	2026-04-13 18:07:16.057159	456.00	456.00	456.00	3.00	0	\N
\.


--
-- Data for Name: proveedores; Type: TABLE DATA; Schema: public; Owner: admin_verde
--

COPY public.proveedores (id, codigo, nombre, contacto, telefono, activo, created_at) FROM stdin;
1	PROV-001	SolarTech SAC	Juan Ríos	01-4567890	t	2026-04-13 18:41:18.481612
2	PROV-002	ElectroImport SRL	María Castro	01-3456789	t	2026-04-13 18:41:18.481612
3	PROV-003	AudioDistrib EIRL	Pedro Luna	01-2345678	t	2026-04-13 18:41:18.481612
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: admin_verde
--

COPY public.usuarios (id, dni, password_hash, nombre, rol, vendedor_id, activo, created_at) FROM stdin;
1	10000001	$2b$12$UogmPwSv57Y95TkiebVwPu2GHe02GIjow6OXaLmDh2IO6T6CWThz6	David	administrador	\N	t	2026-04-18 08:56:28.622407
2	10000002	$2b$12$VGpG7m5PVpFj3NVyddJoMuM9LzePyrPYjfDjkJ0VdGTng952h8GRm	Mayra	vendedor	1	t	2026-04-18 08:56:28.622407
3	10000003	$2b$12$u83n4mr13bVhdGFB/P7rieh4MkXJyBsyPKa03aOo52P5Mmwp61D/i	Christian	logistica	\N	t	2026-04-18 08:56:28.622407
\.


--
-- Data for Name: vendedores; Type: TABLE DATA; Schema: public; Owner: admin_verde
--

COPY public.vendedores (id, codigo, nombre_completo, empresa_id, telefono, activo, created_at) FROM stdin;
1	LUMI-V001	Carlos Mamani Torres	1	987654321	t	2026-04-13 18:07:16.031242
2	LUMI-V002	Rosa Quispe Huanca	1	976543210	t	2026-04-13 18:07:16.031242
3	LUMI-V003	Juan Apaza Lima	1	965432109	t	2026-04-13 18:07:16.031242
4	AUDIO-V001	Pedro Vargas Soto	2	954321098	t	2026-04-13 18:07:16.036454
5	AUDIO-V002	María Condori Ramos	2	943210987	t	2026-04-13 18:07:16.036454
6	AUDIO-V003	Luis Huanca Flores	2	932109876	t	2026-04-13 18:07:16.036454
7	LUMI-V099	Test Vendedor	1	912345678	t	2026-04-13 18:19:23.740004
\.


--
-- Name: agencias_destino_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_verde
--

SELECT pg_catalog.setval('public.agencias_destino_id_seq', 20, true);


--
-- Name: compras_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_verde
--

SELECT pg_catalog.setval('public.compras_id_seq', 7, true);


--
-- Name: detalle_compra_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_verde
--

SELECT pg_catalog.setval('public.detalle_compra_id_seq', 9, true);


--
-- Name: detalle_pedido_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_verde
--

SELECT pg_catalog.setval('public.detalle_pedido_id_seq', 18, true);


--
-- Name: empresas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_verde
--

SELECT pg_catalog.setval('public.empresas_id_seq', 2, true);


--
-- Name: flujo_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_verde
--

SELECT pg_catalog.setval('public.flujo_log_id_seq', 42, true);


--
-- Name: pedidos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_verde
--

SELECT pg_catalog.setval('public.pedidos_id_seq', 16, true);


--
-- Name: productos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_verde
--

SELECT pg_catalog.setval('public.productos_id_seq', 11, true);


--
-- Name: proveedores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_verde
--

SELECT pg_catalog.setval('public.proveedores_id_seq', 3, true);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_verde
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 3, true);


--
-- Name: vendedores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_verde
--

SELECT pg_catalog.setval('public.vendedores_id_seq', 7, true);


--
-- Name: agencias_destino agencias_destino_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.agencias_destino
    ADD CONSTRAINT agencias_destino_pkey PRIMARY KEY (id);


--
-- Name: compras compras_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.compras
    ADD CONSTRAINT compras_pkey PRIMARY KEY (id);


--
-- Name: detalle_compra detalle_compra_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.detalle_compra
    ADD CONSTRAINT detalle_compra_pkey PRIMARY KEY (id);


--
-- Name: detalle_pedido detalle_pedido_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.detalle_pedido
    ADD CONSTRAINT detalle_pedido_pkey PRIMARY KEY (id);


--
-- Name: empresas empresas_codigo_key; Type: CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.empresas
    ADD CONSTRAINT empresas_codigo_key UNIQUE (codigo);


--
-- Name: empresas empresas_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.empresas
    ADD CONSTRAINT empresas_pkey PRIMARY KEY (id);


--
-- Name: flujo_log flujo_log_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.flujo_log
    ADD CONSTRAINT flujo_log_pkey PRIMARY KEY (id);


--
-- Name: pedidos pedidos_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.pedidos
    ADD CONSTRAINT pedidos_pkey PRIMARY KEY (id);


--
-- Name: productos productos_codigo_key; Type: CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_codigo_key UNIQUE (codigo);


--
-- Name: productos productos_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_pkey PRIMARY KEY (id);


--
-- Name: proveedores proveedores_codigo_key; Type: CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.proveedores
    ADD CONSTRAINT proveedores_codigo_key UNIQUE (codigo);


--
-- Name: proveedores proveedores_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.proveedores
    ADD CONSTRAINT proveedores_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_dni_key; Type: CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_dni_key UNIQUE (dni);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: vendedores vendedores_codigo_key; Type: CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.vendedores
    ADD CONSTRAINT vendedores_codigo_key UNIQUE (codigo);


--
-- Name: vendedores vendedores_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.vendedores
    ADD CONSTRAINT vendedores_pkey PRIMARY KEY (id);


--
-- Name: idx_detalle_compra_compra; Type: INDEX; Schema: public; Owner: admin_verde
--

CREATE INDEX idx_detalle_compra_compra ON public.detalle_compra USING btree (compra_id);


--
-- Name: idx_detalle_pedido_pedido; Type: INDEX; Schema: public; Owner: admin_verde
--

CREATE INDEX idx_detalle_pedido_pedido ON public.detalle_pedido USING btree (pedido_id);


--
-- Name: idx_detalle_pedido_producto; Type: INDEX; Schema: public; Owner: admin_verde
--

CREATE INDEX idx_detalle_pedido_producto ON public.detalle_pedido USING btree (producto_id);


--
-- Name: idx_flujo_log_pedido; Type: INDEX; Schema: public; Owner: admin_verde
--

CREATE INDEX idx_flujo_log_pedido ON public.flujo_log USING btree (pedido_id);


--
-- Name: idx_pedidos_empresa; Type: INDEX; Schema: public; Owner: admin_verde
--

CREATE INDEX idx_pedidos_empresa ON public.pedidos USING btree (empresa_id);


--
-- Name: idx_pedidos_estado; Type: INDEX; Schema: public; Owner: admin_verde
--

CREATE INDEX idx_pedidos_estado ON public.pedidos USING btree (estado);


--
-- Name: idx_pedidos_fecha_registro; Type: INDEX; Schema: public; Owner: admin_verde
--

CREATE INDEX idx_pedidos_fecha_registro ON public.pedidos USING btree (fecha_registro);


--
-- Name: idx_pedidos_vendedor; Type: INDEX; Schema: public; Owner: admin_verde
--

CREATE INDEX idx_pedidos_vendedor ON public.pedidos USING btree (vendedor_id);


--
-- Name: idx_productos_empresa; Type: INDEX; Schema: public; Owner: admin_verde
--

CREATE INDEX idx_productos_empresa ON public.productos USING btree (empresa_id);


--
-- Name: idx_vendedores_empresa; Type: INDEX; Schema: public; Owner: admin_verde
--

CREATE INDEX idx_vendedores_empresa ON public.vendedores USING btree (empresa_id);


--
-- Name: compras compras_empresa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.compras
    ADD CONSTRAINT compras_empresa_id_fkey FOREIGN KEY (empresa_id) REFERENCES public.empresas(id);


--
-- Name: compras compras_proveedor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.compras
    ADD CONSTRAINT compras_proveedor_id_fkey FOREIGN KEY (proveedor_id) REFERENCES public.proveedores(id);


--
-- Name: detalle_compra detalle_compra_compra_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.detalle_compra
    ADD CONSTRAINT detalle_compra_compra_id_fkey FOREIGN KEY (compra_id) REFERENCES public.compras(id) ON DELETE CASCADE;


--
-- Name: detalle_compra detalle_compra_producto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.detalle_compra
    ADD CONSTRAINT detalle_compra_producto_id_fkey FOREIGN KEY (producto_id) REFERENCES public.productos(id);


--
-- Name: detalle_pedido detalle_pedido_pedido_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.detalle_pedido
    ADD CONSTRAINT detalle_pedido_pedido_id_fkey FOREIGN KEY (pedido_id) REFERENCES public.pedidos(id) ON DELETE CASCADE;


--
-- Name: detalle_pedido detalle_pedido_producto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.detalle_pedido
    ADD CONSTRAINT detalle_pedido_producto_id_fkey FOREIGN KEY (producto_id) REFERENCES public.productos(id);


--
-- Name: flujo_log flujo_log_pedido_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.flujo_log
    ADD CONSTRAINT flujo_log_pedido_id_fkey FOREIGN KEY (pedido_id) REFERENCES public.pedidos(id);


--
-- Name: pedidos pedidos_agencia_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.pedidos
    ADD CONSTRAINT pedidos_agencia_id_fkey FOREIGN KEY (agencia_id) REFERENCES public.agencias_destino(id);


--
-- Name: pedidos pedidos_empresa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.pedidos
    ADD CONSTRAINT pedidos_empresa_id_fkey FOREIGN KEY (empresa_id) REFERENCES public.empresas(id);


--
-- Name: pedidos pedidos_producto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.pedidos
    ADD CONSTRAINT pedidos_producto_id_fkey FOREIGN KEY (producto_id) REFERENCES public.productos(id);


--
-- Name: pedidos pedidos_vendedor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.pedidos
    ADD CONSTRAINT pedidos_vendedor_id_fkey FOREIGN KEY (vendedor_id) REFERENCES public.vendedores(id);


--
-- Name: productos productos_empresa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_empresa_id_fkey FOREIGN KEY (empresa_id) REFERENCES public.empresas(id);


--
-- Name: usuarios usuarios_vendedor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_vendedor_id_fkey FOREIGN KEY (vendedor_id) REFERENCES public.vendedores(id);


--
-- Name: vendedores vendedores_empresa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_verde
--

ALTER TABLE ONLY public.vendedores
    ADD CONSTRAINT vendedores_empresa_id_fkey FOREIGN KEY (empresa_id) REFERENCES public.empresas(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 3RAQHn7VHfkyfcOAlrRqsnzVXpOZ38U8a77XTaLHbxKkeRaIlfgLUy2MJcuG3LC

