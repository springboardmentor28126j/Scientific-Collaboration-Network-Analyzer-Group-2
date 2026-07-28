--
-- PostgreSQL database dump
--

\restrict apbMgun4qbVaZgdCy9KZB323LEqNaVO5ldGNlTv1HwC9fFNjbgD7HDyIsgnPq5r

-- Dumped from database version 17.10
-- Dumped by pg_dump version 17.10

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: collaborations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.collaborations (
    id integer NOT NULL,
    researcher_1_id integer NOT NULL,
    researcher_2_id integer NOT NULL,
    paper_id integer NOT NULL,
    collaboration_year integer NOT NULL
);


ALTER TABLE public.collaborations OWNER TO postgres;

--
-- Name: collaborations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.collaborations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.collaborations_id_seq OWNER TO postgres;

--
-- Name: collaborations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.collaborations_id_seq OWNED BY public.collaborations.id;


--
-- Name: conferences; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.conferences (
    id integer NOT NULL,
    conference_name character varying NOT NULL,
    organizer character varying NOT NULL,
    venue character varying NOT NULL,
    country character varying NOT NULL,
    conference_date date NOT NULL,
    submission_deadline date NOT NULL,
    registration_deadline date NOT NULL,
    registration_fee integer NOT NULL,
    conference_type character varying NOT NULL,
    website character varying,
    description text,
    topics character varying,
    banner_image character varying,
    brochure_pdf character varying,
    status character varying,
    researcher_id integer
);


ALTER TABLE public.conferences OWNER TO postgres;

--
-- Name: conferences_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.conferences_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.conferences_id_seq OWNER TO postgres;

--
-- Name: conferences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.conferences_id_seq OWNED BY public.conferences.id;


--
-- Name: institutions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.institutions (
    id integer NOT NULL,
    institution_name character varying(150) NOT NULL,
    country character varying(100) NOT NULL,
    city character varying(100) NOT NULL,
    website character varying(200),
    established_year integer
);


ALTER TABLE public.institutions OWNER TO postgres;

--
-- Name: institutions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.institutions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.institutions_id_seq OWNER TO postgres;

--
-- Name: institutions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.institutions_id_seq OWNED BY public.institutions.id;


--
-- Name: research_papers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.research_papers (
    id integer NOT NULL,
    title text,
    authors text,
    abstract text,
    publication_year integer,
    source text,
    doi text,
    keywords character varying(255),
    paper_file character varying(255),
    status character varying(50) DEFAULT 'Draft'::character varying,
    researcher_id integer
);


ALTER TABLE public.research_papers OWNER TO postgres;

--
-- Name: research_papers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.research_papers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.research_papers_id_seq OWNER TO postgres;

--
-- Name: research_papers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.research_papers_id_seq OWNED BY public.research_papers.id;


--
-- Name: researchers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.researchers (
    id integer NOT NULL,
    full_name character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    institution character varying(150) NOT NULL,
    department character varying(100) NOT NULL,
    specialization character varying(100) NOT NULL,
    h_index integer DEFAULT 0,
    total_publications integer DEFAULT 0
);


ALTER TABLE public.researchers OWNER TO postgres;

--
-- Name: researchers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.researchers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.researchers_id_seq OWNER TO postgres;

--
-- Name: researchers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.researchers_id_seq OWNED BY public.researchers.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    full_name character varying(150) NOT NULL,
    username character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    phone_number character varying(20),
    gender character varying(20),
    date_of_birth date,
    institution character varying(150),
    department character varying(100),
    designation character varying(100),
    specialization character varying(150),
    research_interests character varying(255),
    country character varying(100),
    state character varying(100),
    city character varying(100),
    website character varying(255),
    established_year character varying(10),
    institution_type character varying(100),
    role character varying(50)
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: collaborations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collaborations ALTER COLUMN id SET DEFAULT nextval('public.collaborations_id_seq'::regclass);


--
-- Name: conferences id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conferences ALTER COLUMN id SET DEFAULT nextval('public.conferences_id_seq'::regclass);


--
-- Name: institutions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institutions ALTER COLUMN id SET DEFAULT nextval('public.institutions_id_seq'::regclass);


--
-- Name: research_papers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.research_papers ALTER COLUMN id SET DEFAULT nextval('public.research_papers_id_seq'::regclass);


--
-- Name: researchers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.researchers ALTER COLUMN id SET DEFAULT nextval('public.researchers_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: collaborations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.collaborations (id, researcher_1_id, researcher_2_id, paper_id, collaboration_year) FROM stdin;
1	2	2	1	2025
\.


--
-- Data for Name: conferences; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.conferences (id, conference_name, organizer, venue, country, conference_date, submission_deadline, registration_deadline, registration_fee, conference_type, website, description, topics, banner_image, brochure_pdf, status, researcher_id) FROM stdin;
1	IEEE International Conference on AI	IEEE	Hyderabad	India	2026-07-15	2026-07-06	2026-07-08	1500	Offline	https://ieee.org	International conference on Artificial Intelligence and Machine Learning.	AI, ML, Deep Learning	uploads/conferences/BDRC Logo.jpg	uploads/conferences/Baratam Udaya Sri Resume.pdf	Upcoming	2
3	test	prabha	Hyderabad	india	2026-07-08	2026-07-07	2026-07-12	1500	offline	https://adityatekkali.edu.in/autonomous.php	this is to test	 AI, ML	uploads/conferences/BDRC Logo.jpg	uploads/conferences/Baratam Udaya Sri Resume.pdf	upcoming	1
\.


--
-- Data for Name: institutions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.institutions (id, institution_name, country, city, website, established_year) FROM stdin;
1	Malla Reddy University	India	Hyderabad	https://www.mallareddyuniversity.ac.in	2020
2	vit	India	Amaravati	https://vitap.ac.in	1998
\.


--
-- Data for Name: research_papers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.research_papers (id, title, authors, abstract, publication_year, source, doi, keywords, paper_file, status, researcher_id) FROM stdin;
1	Artificial Intelligence in Scientific Collaboration	John Smith	This paper explains how AI improves scientific collaboration and research.	2025	IEEE	10.1000/abc123	\N	\N	Draft	\N
3	Deep Learning for Medical Imaging	Jane Doe	Deep learning techniques for medical image analysis.	2024	Springer	10.1000/abc124	\N	\N	Draft	\N
4	Blockchain in Healthcare	Alice Brown	Blockchain applications for secure healthcare systems.	2023	Elsevier	10.1000/abc125	\N	\N	Draft	\N
5	Machine Learning in Education	David Wilson	Using machine learning to personalize education.	2022	ACM	10.1000/abc126	\N	\N	Draft	\N
6	IoT for Smart Cities	Emily Davis	Internet of Things applications in smart city development.	2021	IEEE	10.1000/abc127	\N	\N	Draft	\N
7	Emotion Aware Adaptive Learning System	Divyasri	AI based adaptive learning platform for personalized education.	2026	IEEE	10.1000/divya001	AI, ML, Education		Draft	1
10	test paper	Divyasri	testing the upload paper	2026	IEEE	10.1000/testpdf001	AI, ML	uploads/09145071-2a4a-4c79-8ab0-5b9a329d193a_BARATAM UDAYA SRI_BioData .pdf	Draft	1
11	testing 	Divyasri	paper upload is testing	2026	IEEE	10.1000/divya001	AI, ML	uploads\\73a42f84-c55e-45f5-bdad-1b3cefa9655c_Baratam Divya Sri Resume.pdf	Draft	1
\.


--
-- Data for Name: researchers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.researchers (id, full_name, email, institution, department, specialization, h_index, total_publications) FROM stdin;
2	Divya Sri	baratamdivyasri@gmail.com	ABC University	AIML	Artificial Intelligence	5	12
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, full_name, username, email, hashed_password, phone_number, gender, date_of_birth, institution, department, designation, specialization, research_interests, country, state, city, website, established_year, institution_type, role) FROM stdin;
3	Udaya	udaya@123	udaya@gamail.com	$2b$12$gv..KeWphn8zHopvFwUBKerCt9CznmaVcPQAFAeBCQ6phfSNkvSOu	 9876543210	Female	2026-07-08						India	Andhra Pradesh	 Srikakulam	https://adityatekkali.edu.in/autonomous.php	1998	College	Institution
1	Divyasri	Divya	baratamdivyasri@gmail.com	$2b$12$fpBSXSzGY6pgbmFeNx4PA.NftZXh3OL39/pDOkqk8Q0dP1o7M8G7G	9876543210	Female	2005-07-08	Aditya Institute of Technology and Management	AIML	Student	Artificial Intelligence	Machine Learning, Deep Learning	India	Andhra Pradesh	Srikakulam	https://github.com/divyasri			Researcher
2	Divya	baratamdivyasri@gmail.com	23a51a4207@adityatekkali.edu.in	$2b$12$yI5YqHlv5JXV95S4ai5j4ugri/3xjqqhB5r5krhchXnGLaj8lNpem	 9876543210	Female	2026-07-09	Aditya Institute of Technology and Management	AIML	Student	Artificial Intelligence	Machine Learning, Deep Learning	India	Andhra Pradesh	 Srikakulam	https://adityatekkali.edu.in/autonomous.php			Researcher
\.


--
-- Name: collaborations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.collaborations_id_seq', 2, true);


--
-- Name: conferences_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.conferences_id_seq', 3, true);


--
-- Name: institutions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.institutions_id_seq', 2, true);


--
-- Name: research_papers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.research_papers_id_seq', 11, true);


--
-- Name: researchers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.researchers_id_seq', 2, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 3, true);


--
-- Name: collaborations collaborations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collaborations
    ADD CONSTRAINT collaborations_pkey PRIMARY KEY (id);


--
-- Name: conferences conferences_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conferences
    ADD CONSTRAINT conferences_pkey PRIMARY KEY (id);


--
-- Name: institutions institutions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institutions
    ADD CONSTRAINT institutions_pkey PRIMARY KEY (id);


--
-- Name: research_papers research_papers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.research_papers
    ADD CONSTRAINT research_papers_pkey PRIMARY KEY (id);


--
-- Name: researchers researchers_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.researchers
    ADD CONSTRAINT researchers_email_key UNIQUE (email);


--
-- Name: researchers researchers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.researchers
    ADD CONSTRAINT researchers_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: ix_conferences_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_conferences_id ON public.conferences USING btree (id);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: conferences conferences_researcher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conferences
    ADD CONSTRAINT conferences_researcher_id_fkey FOREIGN KEY (researcher_id) REFERENCES public.users(id);


--
-- Name: collaborations fk_paper; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collaborations
    ADD CONSTRAINT fk_paper FOREIGN KEY (paper_id) REFERENCES public.research_papers(id) ON DELETE CASCADE;


--
-- Name: research_papers fk_researcher; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.research_papers
    ADD CONSTRAINT fk_researcher FOREIGN KEY (researcher_id) REFERENCES public.users(id);


--
-- Name: collaborations fk_researcher1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collaborations
    ADD CONSTRAINT fk_researcher1 FOREIGN KEY (researcher_1_id) REFERENCES public.researchers(id) ON DELETE CASCADE;


--
-- Name: collaborations fk_researcher2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collaborations
    ADD CONSTRAINT fk_researcher2 FOREIGN KEY (researcher_2_id) REFERENCES public.researchers(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict apbMgun4qbVaZgdCy9KZB323LEqNaVO5ldGNlTv1HwC9fFNjbgD7HDyIsgnPq5r

