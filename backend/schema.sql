--
-- PostgreSQL database dump
--

\restrict mJR5OcL4qtmNjj0IiTERvNCmfCaRHJexqXdzt7ATGJ0815H9RrN0LaSfSV6rUvW

-- Dumped from database version 18.3 (Debian 18.3-1.pgdg13+1)
-- Dumped by pg_dump version 18.3 (Debian 18.3-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.restaurante DROP CONSTRAINT IF EXISTS restaurante_id_usuario_fkey;
ALTER TABLE IF EXISTS ONLY public.reservas DROP CONSTRAINT IF EXISTS reservas_usuario_id_fkey;
ALTER TABLE IF EXISTS ONLY public.reservas DROP CONSTRAINT IF EXISTS reservas_id_mesa_fkey;
ALTER TABLE IF EXISTS ONLY public.mesa DROP CONSTRAINT IF EXISTS mesa_id_restaurante_fkey;
ALTER TABLE IF EXISTS ONLY public.horario DROP CONSTRAINT IF EXISTS horario_id_restaurante_fkey;
ALTER TABLE IF EXISTS ONLY public.usuarios DROP CONSTRAINT IF EXISTS usuarios_pkey;
ALTER TABLE IF EXISTS ONLY public.usuarios DROP CONSTRAINT IF EXISTS usuarios_correo_key;
ALTER TABLE IF EXISTS ONLY public.restaurante DROP CONSTRAINT IF EXISTS restaurante_pkey;
ALTER TABLE IF EXISTS ONLY public.reservas DROP CONSTRAINT IF EXISTS reservas_pkey;
ALTER TABLE IF EXISTS ONLY public.mesa DROP CONSTRAINT IF EXISTS mesa_pkey;
ALTER TABLE IF EXISTS ONLY public.mesa DROP CONSTRAINT IF EXISTS mesa_id_restaurante_numero_mesa_key;
ALTER TABLE IF EXISTS ONLY public.horario DROP CONSTRAINT IF EXISTS horario_pkey;
ALTER TABLE IF EXISTS ONLY public.horario DROP CONSTRAINT IF EXISTS horario_id_restaurante_dia_semana_key;
ALTER TABLE IF EXISTS public.usuarios ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.restaurante ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.reservas ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.mesa ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.horario ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.usuarios_id_seq;
DROP TABLE IF EXISTS public.usuarios;
DROP SEQUENCE IF EXISTS public.restaurante_id_seq;
DROP TABLE IF EXISTS public.restaurante;
DROP SEQUENCE IF EXISTS public.reservas_id_seq;
DROP TABLE IF EXISTS public.reservas;
DROP SEQUENCE IF EXISTS public.mesa_id_seq;
DROP TABLE IF EXISTS public.mesa;
DROP SEQUENCE IF EXISTS public.horario_id_seq;
DROP TABLE IF EXISTS public.horario;
DROP TYPE IF EXISTS public.dia_semana_enum;
--
-- Name: dia_semana_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.dia_semana_enum AS ENUM (
    'lunes',
    'martes',
    'miércoles',
    'jueves',
    'viernes',
    'sábado',
    'domingo'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: horario; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.horario (
    id integer NOT NULL,
    id_restaurante integer NOT NULL,
    dia_semana public.dia_semana_enum NOT NULL,
    hora_apertura time without time zone NOT NULL,
    hora_cierre time without time zone NOT NULL
);


--
-- Name: horario_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.horario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: horario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.horario_id_seq OWNED BY public.horario.id;


--
-- Name: mesa; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mesa (
    id integer NOT NULL,
    id_restaurante integer NOT NULL,
    numero_mesa integer NOT NULL,
    capacidad integer NOT NULL,
    disponible boolean DEFAULT true NOT NULL,
    CONSTRAINT mesa_capacidad_check CHECK ((capacidad > 0))
);


--
-- Name: mesa_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.mesa_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: mesa_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.mesa_id_seq OWNED BY public.mesa.id;


--
-- Name: reservas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reservas (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    id_mesa integer,
    fecha date NOT NULL,
    hora time without time zone NOT NULL,
    personas integer NOT NULL,
    estado character varying(20) DEFAULT 'pendiente'::character varying
);


--
-- Name: reservas_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.reservas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: reservas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.reservas_id_seq OWNED BY public.reservas.id;


--
-- Name: restaurante; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.restaurante (
    id integer NOT NULL,
    id_usuario integer NOT NULL,
    nombre character varying(120) NOT NULL,
    direccion character varying(255) NOT NULL,
    telefono character varying(20),
    descripcion text
);


--
-- Name: restaurante_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.restaurante_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: restaurante_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.restaurante_id_seq OWNED BY public.restaurante.id;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    correo character varying(150) NOT NULL,
    password character varying(255) NOT NULL,
    rol character varying(20) DEFAULT 'cliente'::character varying NOT NULL,
    fecha timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- Name: horario id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.horario ALTER COLUMN id SET DEFAULT nextval('public.horario_id_seq'::regclass);


--
-- Name: mesa id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mesa ALTER COLUMN id SET DEFAULT nextval('public.mesa_id_seq'::regclass);


--
-- Name: reservas id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reservas ALTER COLUMN id SET DEFAULT nextval('public.reservas_id_seq'::regclass);


--
-- Name: restaurante id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.restaurante ALTER COLUMN id SET DEFAULT nextval('public.restaurante_id_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- Data for Name: horario; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.horario (id, id_restaurante, dia_semana, hora_apertura, hora_cierre) FROM stdin;
1	1	lunes	10:00:00	22:00:00
2	1	martes	10:00:00	22:00:00
3	1	miércoles	10:00:00	22:00:00
4	1	jueves	10:00:00	22:00:00
5	1	viernes	10:00:00	23:00:00
6	1	sábado	10:00:00	23:00:00
7	1	domingo	11:00:00	21:00:00
8	2	lunes	09:00:00	21:00:00
9	2	martes	09:00:00	21:00:00
10	2	miércoles	09:00:00	21:00:00
11	2	jueves	09:00:00	21:00:00
12	2	viernes	09:00:00	22:00:00
13	2	sábado	09:00:00	22:00:00
14	2	domingo	10:00:00	21:00:00
15	3	lunes	08:00:00	20:00:00
16	3	martes	08:00:00	20:00:00
17	3	miércoles	08:00:00	20:00:00
18	3	jueves	08:00:00	20:00:00
19	3	viernes	08:00:00	21:00:00
20	3	sábado	08:00:00	21:00:00
21	4	lunes	11:00:00	22:00:00
22	4	martes	11:00:00	22:00:00
23	4	miércoles	11:00:00	22:00:00
24	4	jueves	11:00:00	22:00:00
25	4	viernes	11:00:00	23:00:00
26	4	sábado	11:00:00	23:00:00
27	4	domingo	12:00:00	21:00:00
\.


--
-- Data for Name: mesa; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.mesa (id, id_restaurante, numero_mesa, capacidad, disponible) FROM stdin;
1	1	1	2	t
2	1	2	4	t
3	1	3	4	t
4	1	4	6	t
5	2	1	2	t
6	2	2	4	t
7	2	3	4	t
8	2	4	8	t
9	3	1	2	t
10	3	2	4	t
11	3	3	6	t
12	4	1	2	t
13	4	2	4	t
14	4	3	4	t
15	4	4	6	t
\.


--
-- Data for Name: reservas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.reservas (id, usuario_id, id_mesa, fecha, hora, personas, estado) FROM stdin;
1	3	5	2026-04-30	19:56:00	2	cancelada
2	3	10	2026-04-30	16:30:00	4	pendiente
3	4	5	2026-05-01	15:58:00	2	pendiente
4	3	1	2026-04-05	16:00:00	2	pendiente
5	3	15	2026-05-04	12:30:00	1	cancelada
6	3	15	2026-05-04	12:30:00	5	cancelada
7	3	15	2026-05-04	12:30:00	5	pendiente
8	3	6	2026-05-04	12:29:00	4	pendiente
9	3	8	2026-05-05	23:50:00	5	pendiente
10	3	6	2026-05-04	12:29:00	4	pendiente
11	3	1	2026-05-04	14:25:00	2	pendiente
12	3	10	2026-05-08	16:30:00	4	pendiente
13	5	15	2026-10-30	14:00:00	5	pendiente
\.


--
-- Data for Name: restaurante; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.restaurante (id, id_usuario, nombre, direccion, telefono, descripcion) FROM stdin;
1	1	Crepes & Waffles	Centro Comercial Unicentro, Pereira	3101111111	Cocina internacional, crepes dulces y salados
2	1	Frisby	Carrera 8 #18-32, Pereira	3102222222	Pollo frito estilo colombiano
3	1	Salchipaisa	Calle 19 #6-10, Pereira	3103333333	Comida típica paisa, salchipapas y más
4	1	Dragón de Oro	Carrera 10 #15-40, Pereira	3104444444	Restaurante de comida china, especialidad en arroz
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.usuarios (id, nombre, correo, password, rol, fecha) FROM stdin;
2	Admin ReserVibe	admin@reservibe.com	$2b$12$VbZQ2rNffGoizksY222LWu7WrGoSphY8e6RhhfMxVR44ewe65..0y	cliente	2026-04-28 00:18:19.204883
1	Santiago	santiago@gmail.com	$2b$12$IX3/EdFZ.LA8epTy2WEWl.TIPRwoLmyB6Y/ve1TOVBooWzTih4BBS	admin	2026-04-28 00:09:24.432408
3	Santiago Aristizabal	aristizabal7@gmail.com	$2b$12$UD5.nzvYvFH3jddbNDVNc.f/U7P5ibnnjVPmkNtNqp3Sp/Dbrg5d2	cliente	2026-04-28 18:50:43.49756
4	Mariana	mari2401@gmail.com	$2b$12$a5RuzgUI6YvqHaXXs8/bY.2P7SPxq.Jsy63oBLqZGemlEG7o9ldhO	cliente	2026-05-01 17:57:05.390926
5	Juan Felipe Londoño	Juanfelipelondonomarin@gmail.com	$2b$12$OrLfuadBFeSfNYPZtI0O5.HhgX4nd7zlwKx/W7WkSdVeyhqc6BWwO	cliente	2026-05-07 00:09:32.325067
\.


--
-- Name: horario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.horario_id_seq', 27, true);


--
-- Name: mesa_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.mesa_id_seq', 15, true);


--
-- Name: reservas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.reservas_id_seq', 13, true);


--
-- Name: restaurante_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.restaurante_id_seq', 4, true);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 5, true);


--
-- Name: horario horario_id_restaurante_dia_semana_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.horario
    ADD CONSTRAINT horario_id_restaurante_dia_semana_key UNIQUE (id_restaurante, dia_semana);


--
-- Name: horario horario_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.horario
    ADD CONSTRAINT horario_pkey PRIMARY KEY (id);


--
-- Name: mesa mesa_id_restaurante_numero_mesa_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mesa
    ADD CONSTRAINT mesa_id_restaurante_numero_mesa_key UNIQUE (id_restaurante, numero_mesa);


--
-- Name: mesa mesa_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mesa
    ADD CONSTRAINT mesa_pkey PRIMARY KEY (id);


--
-- Name: reservas reservas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_pkey PRIMARY KEY (id);


--
-- Name: restaurante restaurante_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.restaurante
    ADD CONSTRAINT restaurante_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_correo_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_correo_key UNIQUE (correo);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: horario horario_id_restaurante_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.horario
    ADD CONSTRAINT horario_id_restaurante_fkey FOREIGN KEY (id_restaurante) REFERENCES public.restaurante(id) ON DELETE CASCADE;


--
-- Name: mesa mesa_id_restaurante_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mesa
    ADD CONSTRAINT mesa_id_restaurante_fkey FOREIGN KEY (id_restaurante) REFERENCES public.restaurante(id) ON DELETE CASCADE;


--
-- Name: reservas reservas_id_mesa_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_id_mesa_fkey FOREIGN KEY (id_mesa) REFERENCES public.mesa(id);


--
-- Name: reservas reservas_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);


--
-- Name: restaurante restaurante_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.restaurante
    ADD CONSTRAINT restaurante_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id);


--
-- PostgreSQL database dump complete
--

\unrestrict mJR5OcL4qtmNjj0IiTERvNCmfCaRHJexqXdzt7ATGJ0815H9RrN0LaSfSV6rUvW

