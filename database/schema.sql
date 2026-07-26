-- Schema logico finale FlowForest
<<<<<<< HEAD
-- Generato dal database PostgreSQL tramite tools/export_schema.py.
=======
-- Generato dal database PostgreSQL tramite genera_schema_finale.py.
>>>>>>> 6ba68938b2dbe185ec02630b4ad91749e1d79b49
-- Non contiene dati né credenziali.

BEGIN;

CREATE SCHEMA IF NOT EXISTS public;
SET search_path TO public;

CREATE SEQUENCE public."cliente_flowforest_id_cliente_seq"
    AS integer
    INCREMENT BY 1
    MINVALUE 1
    MAXVALUE 2147483647
    START WITH 1
    CACHE 1
    NO CYCLE;

CREATE SEQUENCE public."evento_id_evento_seq"
    AS integer
    INCREMENT BY 1
    MINVALUE 1
    MAXVALUE 2147483647
    START WITH 1
    CACHE 1
    NO CYCLE;

CREATE SEQUENCE public."feedback_id_feedback_seq"
    AS integer
    INCREMENT BY 1
    MINVALUE 1
    MAXVALUE 2147483647
    START WITH 1
    CACHE 1
    NO CYCLE;

CREATE SEQUENCE public."modulo_didattico_id_modulo_seq"
    AS integer
    INCREMENT BY 1
    MINVALUE 1
    MAXVALUE 2147483647
    START WITH 1
    CACHE 1
    NO CYCLE;

CREATE SEQUENCE public."risorsa_umana_id_dipendente_seq"
    AS integer
    INCREMENT BY 1
    MINVALUE 1
    MAXVALUE 2147483647
    START WITH 1
    CACHE 1
    NO CYCLE;

CREATE TABLE public."amministrativo" (
    "id_dipendente" integer NOT NULL
);

CREATE TABLE public."area" (
    "nome" character varying(50) NOT NULL,
    "capienza" integer NOT NULL,
    "scopo" character varying(100)
);

CREATE TABLE public."attrezzatura" (
    "codice_articolo" character varying(50) NOT NULL,
    "stato_usura" character varying(20),
    "data_ultimo_utilizzo" date
);

CREATE TABLE public."azienda_cliente" (
    "p_iva" character varying(11) NOT NULL,
    "nome_azienda" character varying(100) NOT NULL,
    "pec_fatturazione" character varying(100) NOT NULL,
    "email" character varying(100) NOT NULL
);

CREATE TABLE public."azienda_partner" (
    "id_cliente" integer NOT NULL,
    "p_iva" character varying(11) NOT NULL,
    "nome_azienda" character varying(100) NOT NULL,
    "specializzazione" character varying(100),
    "email" character varying(100) NOT NULL
);

CREATE TABLE public."biglietto_persona" (
    "cod_seriale" character varying(50) NOT NULL,
    "data_emissione" date DEFAULT CURRENT_DATE NOT NULL,
    "richiesta_allergie" character varying(255),
    "biglietto_aziendale" boolean DEFAULT false NOT NULL,
    "prezzo_pagato" numeric(10,2) NOT NULL,
    "id_evento" integer NOT NULL,
    "p_iva_azienda" character varying(11),
    "codice_fiscale" character varying(16) NOT NULL
);

CREATE TABLE public."cliente_flowforest" (
    "id_cliente" integer DEFAULT nextval('cliente_flowforest_id_cliente_seq'::regclass) NOT NULL,
    "data_registrazione" date DEFAULT CURRENT_DATE NOT NULL
);

CREATE TABLE public."consumabile" (
    "codice_articolo" character varying(50) NOT NULL,
    "data_scadenza" date NOT NULL,
    "allergeni_presenti" character varying(255)
);

CREATE TABLE public."dettaglio_ordine" (
    "n_ordine" character varying(50) NOT NULL,
    "codice_articolo" character varying(50) NOT NULL,
    "quantita" integer NOT NULL
);

CREATE TABLE public."evento" (
    "id_evento" integer DEFAULT nextval('evento_id_evento_seq'::regclass) NOT NULL,
    "data_inizio" timestamp without time zone NOT NULL,
    "data_fine" timestamp without time zone NOT NULL,
    "partecipanti_max" integer NOT NULL
);

CREATE TABLE public."evento_area" (
    "id_evento" integer NOT NULL,
    "nome_area" character varying(50) NOT NULL
);

CREATE TABLE public."evento_partner" (
    "id_evento" integer NOT NULL,
    "titolo" character varying(100) NOT NULL,
    "id_partner" integer NOT NULL
);

CREATE TABLE public."feedback" (
    "id_feedback" integer DEFAULT nextval('feedback_id_feedback_seq'::regclass) NOT NULL,
    "voto" integer NOT NULL,
    "commento" text,
    "data_compilazione" date DEFAULT CURRENT_DATE NOT NULL,
    "cod_seriale" character varying(50) NOT NULL
);

CREATE TABLE public."formatore" (
    "id_dipendente" integer NOT NULL,
    "certificazioni_attive" text
);

CREATE TABLE public."fornitore" (
    "p_iva" character varying(11) NOT NULL,
    "ragione_sociale" character varying(100) NOT NULL
);

CREATE TABLE public."impiego_materiale" (
    "codice_articolo" character varying(50) NOT NULL,
    "id_evento" integer NOT NULL,
    "quantita_impiegata" integer NOT NULL
);

CREATE TABLE public."laboratorio" (
    "id_evento" integer NOT NULL,
    "codice_lab" character varying(50) NOT NULL,
    "titolo" character varying(100) NOT NULL,
    "descrizione" text,
    "protocollo_op" character varying(100),
    "costo_biglietto" numeric NOT NULL
);

CREATE TABLE public."laboratorio_modulo" (
    "id_evento" integer NOT NULL,
    "id_modulo" integer NOT NULL
);

CREATE TABLE public."materiale" (
    "codice_articolo" character varying(50) NOT NULL,
    "nome_materiale" character varying(100) NOT NULL,
    "quantita_inventario" integer DEFAULT 0 NOT NULL,
    "soglia_minima_riordino" integer DEFAULT 0 NOT NULL
);

CREATE TABLE public."modulo_didattico" (
    "id_modulo" integer DEFAULT nextval('modulo_didattico_id_modulo_seq'::regclass) NOT NULL,
    "nome" character varying(100) NOT NULL,
    "testo" text NOT NULL
);

CREATE TABLE public."operaio" (
    "id_dipendente" integer NOT NULL
);

CREATE TABLE public."ordine" (
    "n_ordine" character varying(50) NOT NULL,
    "data_ordine" date DEFAULT CURRENT_DATE NOT NULL,
    "importo_totale" numeric(10,2) NOT NULL,
    "stato_consegna" character varying(20),
    "p_iva_fornitore" character varying(11) NOT NULL
);

CREATE TABLE public."persona" (
    "codice_fiscale" character varying(16) NOT NULL,
    "nome" character varying(50) NOT NULL,
    "cognome" character varying(50) NOT NULL,
    "note_allergia" character varying(255),
    "data_nascita" date NOT NULL,
    "telefono" character varying(20),
    "mail" character varying(100) NOT NULL,
    "contatto_emergenza" character varying(50),
    "password" text NOT NULL
);

CREATE TABLE public."persona_cliente" (
    "id_cliente" integer NOT NULL,
    "codice_fiscale" character varying(16) NOT NULL
);

CREATE TABLE public."risorsa_umana" (
    "id_dipendente" integer DEFAULT nextval('risorsa_umana_id_dipendente_seq'::regclass) NOT NULL,
    "iban" character varying(27) NOT NULL,
    "data_assunzione" date NOT NULL,
    "codice_fiscale" character varying(16) NOT NULL,
    "mansione" character varying(150),
    "livello_salariale" character varying(20)
);

CREATE TABLE public."struttura" (
    "codice_struttura" character varying(50) NOT NULL,
    "funzione_uso" character varying(100),
    "nome_area" character varying(50) NOT NULL
);

ALTER TABLE ONLY public."amministrativo"
    ADD CONSTRAINT "amministrativo_pkey" PRIMARY KEY (id_dipendente);

ALTER TABLE ONLY public."area"
    ADD CONSTRAINT "area_pkey" PRIMARY KEY (nome);

ALTER TABLE ONLY public."attrezzatura"
    ADD CONSTRAINT "attrezzatura_pkey" PRIMARY KEY (codice_articolo);

ALTER TABLE ONLY public."azienda_cliente"
    ADD CONSTRAINT "azienda_cliente_pkey" PRIMARY KEY (p_iva);

ALTER TABLE ONLY public."azienda_partner"
    ADD CONSTRAINT "azienda_partner_pkey" PRIMARY KEY (id_cliente);

ALTER TABLE ONLY public."biglietto_persona"
    ADD CONSTRAINT "biglietto_persona_pkey" PRIMARY KEY (cod_seriale);

ALTER TABLE ONLY public."cliente_flowforest"
    ADD CONSTRAINT "cliente_flowforest_pkey" PRIMARY KEY (id_cliente);

ALTER TABLE ONLY public."consumabile"
    ADD CONSTRAINT "consumabile_pkey" PRIMARY KEY (codice_articolo);

ALTER TABLE ONLY public."dettaglio_ordine"
    ADD CONSTRAINT "dettaglio_ordine_pkey" PRIMARY KEY (n_ordine, codice_articolo);

ALTER TABLE ONLY public."evento"
    ADD CONSTRAINT "evento_pkey" PRIMARY KEY (id_evento);

ALTER TABLE ONLY public."evento_area"
    ADD CONSTRAINT "evento_area_pkey" PRIMARY KEY (id_evento, nome_area);

ALTER TABLE ONLY public."evento_partner"
    ADD CONSTRAINT "evento_partner_pkey" PRIMARY KEY (id_evento);

ALTER TABLE ONLY public."feedback"
    ADD CONSTRAINT "feedback_pkey" PRIMARY KEY (id_feedback);

ALTER TABLE ONLY public."formatore"
    ADD CONSTRAINT "formatore_pkey" PRIMARY KEY (id_dipendente);

ALTER TABLE ONLY public."fornitore"
    ADD CONSTRAINT "fornitore_pkey" PRIMARY KEY (p_iva);

ALTER TABLE ONLY public."impiego_materiale"
    ADD CONSTRAINT "impiego_materiale_pkey" PRIMARY KEY (id_evento, codice_articolo);

ALTER TABLE ONLY public."laboratorio"
    ADD CONSTRAINT "laboratorio_pkey" PRIMARY KEY (id_evento);

ALTER TABLE ONLY public."laboratorio_modulo"
    ADD CONSTRAINT "laboratorio_modulo_pkey" PRIMARY KEY (id_evento, id_modulo);

ALTER TABLE ONLY public."materiale"
    ADD CONSTRAINT "materiale_pkey" PRIMARY KEY (codice_articolo);

ALTER TABLE ONLY public."modulo_didattico"
    ADD CONSTRAINT "modulo_didattico_pkey" PRIMARY KEY (id_modulo);

ALTER TABLE ONLY public."operaio"
    ADD CONSTRAINT "operaio_pkey" PRIMARY KEY (id_dipendente);

ALTER TABLE ONLY public."ordine"
    ADD CONSTRAINT "ordine_pkey" PRIMARY KEY (n_ordine);

ALTER TABLE ONLY public."persona"
    ADD CONSTRAINT "persona_pkey" PRIMARY KEY (codice_fiscale);

ALTER TABLE ONLY public."persona_cliente"
    ADD CONSTRAINT "persona_cliente_pkey" PRIMARY KEY (id_cliente);

ALTER TABLE ONLY public."risorsa_umana"
    ADD CONSTRAINT "risorsa_umana_pkey" PRIMARY KEY (id_dipendente);

ALTER TABLE ONLY public."struttura"
    ADD CONSTRAINT "struttura_pkey" PRIMARY KEY (codice_struttura);

ALTER TABLE ONLY public."azienda_cliente"
    ADD CONSTRAINT "azienda_cliente_email_key" UNIQUE (email);

ALTER TABLE ONLY public."azienda_cliente"
    ADD CONSTRAINT "azienda_cliente_pec_fatturazione_key" UNIQUE (pec_fatturazione);

ALTER TABLE ONLY public."azienda_partner"
    ADD CONSTRAINT "azienda_partner_email_key" UNIQUE (email);

ALTER TABLE ONLY public."azienda_partner"
    ADD CONSTRAINT "azienda_partner_p_iva_key" UNIQUE (p_iva);

ALTER TABLE ONLY public."feedback"
    ADD CONSTRAINT "feedback_cod_seriale_key" UNIQUE (cod_seriale);

ALTER TABLE ONLY public."laboratorio"
    ADD CONSTRAINT "laboratorio_codice_lab_key" UNIQUE (codice_lab);

ALTER TABLE ONLY public."materiale"
    ADD CONSTRAINT "materiale_nome_materiale_key" UNIQUE (nome_materiale);

ALTER TABLE ONLY public."modulo_didattico"
    ADD CONSTRAINT "modulo_didattico_nome_key" UNIQUE (nome);

ALTER TABLE ONLY public."persona"
    ADD CONSTRAINT "persona_mail_key" UNIQUE (mail);

ALTER TABLE ONLY public."persona_cliente"
    ADD CONSTRAINT "persona_cliente_codice_fiscale_key" UNIQUE (codice_fiscale);

ALTER TABLE ONLY public."risorsa_umana"
    ADD CONSTRAINT "risorsa_umana_codice_fiscale_key" UNIQUE (codice_fiscale);

ALTER TABLE ONLY public."area"
    ADD CONSTRAINT "area_capienza_check" CHECK (capienza > 0);

ALTER TABLE ONLY public."attrezzatura"
    ADD CONSTRAINT "attrezzatura_stato_usura_check" CHECK (stato_usura::text = ANY (ARRAY['Nuovo'::character varying, 'Buono'::character varying, 'Usurato'::character varying, 'Da Sostituire'::character varying]::text[]));

ALTER TABLE ONLY public."biglietto_persona"
    ADD CONSTRAINT "biglietto_persona_prezzo_pagato_check" CHECK (prezzo_pagato >= 0::numeric);

ALTER TABLE ONLY public."dettaglio_ordine"
    ADD CONSTRAINT "dettaglio_ordine_quantita_check" CHECK (quantita > 0);

ALTER TABLE ONLY public."evento"
    ADD CONSTRAINT "evento_check" CHECK (data_fine > data_inizio);

ALTER TABLE ONLY public."evento"
    ADD CONSTRAINT "evento_partecipanti_max_check" CHECK (partecipanti_max > 0);

ALTER TABLE ONLY public."feedback"
    ADD CONSTRAINT "feedback_voto_check" CHECK (voto >= 1 AND voto <= 5);

ALTER TABLE ONLY public."impiego_materiale"
    ADD CONSTRAINT "impiego_materiale_quantita_impiegata_check" CHECK (quantita_impiegata > 0);

ALTER TABLE ONLY public."laboratorio"
    ADD CONSTRAINT "laboratorio_costo_biglietto_check" CHECK (costo_biglietto >= 0::numeric);

ALTER TABLE ONLY public."materiale"
    ADD CONSTRAINT "materiale_quantita_inventario_check" CHECK (quantita_inventario >= 0);

ALTER TABLE ONLY public."materiale"
    ADD CONSTRAINT "materiale_soglia_minima_riordino_check" CHECK (soglia_minima_riordino >= 0);

ALTER TABLE ONLY public."ordine"
    ADD CONSTRAINT "ordine_importo_totale_check" CHECK (importo_totale >= 0::numeric);

ALTER TABLE ONLY public."ordine"
    ADD CONSTRAINT "ordine_stato_consegna_check" CHECK (stato_consegna::text = ANY (ARRAY['In Elaborazione'::character varying, 'Spedito'::character varying, 'Consegnato'::character varying, 'Annullato'::character varying]::text[]));

ALTER SEQUENCE public."cliente_flowforest_id_cliente_seq"
    OWNED BY public."cliente_flowforest"."id_cliente";

ALTER SEQUENCE public."evento_id_evento_seq"
    OWNED BY public."evento"."id_evento";

ALTER SEQUENCE public."feedback_id_feedback_seq"
    OWNED BY public."feedback"."id_feedback";

ALTER SEQUENCE public."modulo_didattico_id_modulo_seq"
    OWNED BY public."modulo_didattico"."id_modulo";

ALTER SEQUENCE public."risorsa_umana_id_dipendente_seq"
    OWNED BY public."risorsa_umana"."id_dipendente";

ALTER TABLE ONLY public."amministrativo"
    ADD CONSTRAINT "amministrativo_id_dipendente_fkey" FOREIGN KEY (id_dipendente) REFERENCES risorsa_umana(id_dipendente) ON DELETE CASCADE;

ALTER TABLE ONLY public."attrezzatura"
    ADD CONSTRAINT "attrezzatura_codice_articolo_fkey" FOREIGN KEY (codice_articolo) REFERENCES materiale(codice_articolo) ON DELETE CASCADE;

ALTER TABLE ONLY public."azienda_partner"
    ADD CONSTRAINT "azienda_partner_id_cliente_fkey" FOREIGN KEY (id_cliente) REFERENCES cliente_flowforest(id_cliente) ON DELETE CASCADE;

ALTER TABLE ONLY public."biglietto_persona"
    ADD CONSTRAINT "biglietto_persona_codice_fiscale_fkey" FOREIGN KEY (codice_fiscale) REFERENCES persona(codice_fiscale) ON DELETE RESTRICT;

ALTER TABLE ONLY public."biglietto_persona"
    ADD CONSTRAINT "biglietto_persona_id_evento_fkey" FOREIGN KEY (id_evento) REFERENCES evento(id_evento) ON DELETE RESTRICT;

ALTER TABLE ONLY public."biglietto_persona"
    ADD CONSTRAINT "biglietto_persona_p_iva_azienda_fkey" FOREIGN KEY (p_iva_azienda) REFERENCES azienda_cliente(p_iva) ON DELETE RESTRICT;

ALTER TABLE ONLY public."consumabile"
    ADD CONSTRAINT "consumabile_codice_articolo_fkey" FOREIGN KEY (codice_articolo) REFERENCES materiale(codice_articolo) ON DELETE CASCADE;

ALTER TABLE ONLY public."dettaglio_ordine"
    ADD CONSTRAINT "dettaglio_ordine_codice_articolo_fkey" FOREIGN KEY (codice_articolo) REFERENCES consumabile(codice_articolo) ON DELETE RESTRICT;

ALTER TABLE ONLY public."dettaglio_ordine"
    ADD CONSTRAINT "dettaglio_ordine_n_ordine_fkey" FOREIGN KEY (n_ordine) REFERENCES ordine(n_ordine) ON DELETE CASCADE;

ALTER TABLE ONLY public."evento_area"
    ADD CONSTRAINT "evento_area_area_fkey" FOREIGN KEY (nome_area) REFERENCES area(nome) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE ONLY public."evento_area"
    ADD CONSTRAINT "evento_area_evento_fkey" FOREIGN KEY (id_evento) REFERENCES evento(id_evento) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public."evento_partner"
    ADD CONSTRAINT "evento_partner_id_evento_fkey" FOREIGN KEY (id_evento) REFERENCES evento(id_evento) ON DELETE CASCADE;

ALTER TABLE ONLY public."evento_partner"
    ADD CONSTRAINT "evento_partner_id_partner_fkey" FOREIGN KEY (id_partner) REFERENCES azienda_partner(id_cliente) ON DELETE RESTRICT;

ALTER TABLE ONLY public."feedback"
    ADD CONSTRAINT "feedback_cod_seriale_fkey" FOREIGN KEY (cod_seriale) REFERENCES biglietto_persona(cod_seriale) ON DELETE CASCADE;

ALTER TABLE ONLY public."formatore"
    ADD CONSTRAINT "formatore_id_dipendente_fkey" FOREIGN KEY (id_dipendente) REFERENCES risorsa_umana(id_dipendente) ON DELETE CASCADE;

ALTER TABLE ONLY public."impiego_materiale"
    ADD CONSTRAINT "impiego_materiale_codice_articolo_fkey" FOREIGN KEY (codice_articolo) REFERENCES materiale(codice_articolo) ON DELETE RESTRICT;

ALTER TABLE ONLY public."impiego_materiale"
    ADD CONSTRAINT "impiego_materiale_id_evento_fkey" FOREIGN KEY (id_evento) REFERENCES evento(id_evento) ON DELETE CASCADE;

ALTER TABLE ONLY public."laboratorio"
    ADD CONSTRAINT "laboratorio_id_evento_fkey" FOREIGN KEY (id_evento) REFERENCES evento(id_evento) ON DELETE CASCADE;

ALTER TABLE ONLY public."laboratorio_modulo"
    ADD CONSTRAINT "laboratorio_modulo_laboratorio_fkey" FOREIGN KEY (id_evento) REFERENCES laboratorio(id_evento) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public."laboratorio_modulo"
    ADD CONSTRAINT "laboratorio_modulo_modulo_fkey" FOREIGN KEY (id_modulo) REFERENCES modulo_didattico(id_modulo) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE ONLY public."operaio"
    ADD CONSTRAINT "operaio_id_dipendente_fkey" FOREIGN KEY (id_dipendente) REFERENCES risorsa_umana(id_dipendente) ON DELETE CASCADE;

ALTER TABLE ONLY public."ordine"
    ADD CONSTRAINT "ordine_p_iva_fornitore_fkey" FOREIGN KEY (p_iva_fornitore) REFERENCES fornitore(p_iva) ON DELETE RESTRICT;

ALTER TABLE ONLY public."persona_cliente"
    ADD CONSTRAINT "persona_cliente_codice_fiscale_fkey" FOREIGN KEY (codice_fiscale) REFERENCES persona(codice_fiscale) ON DELETE RESTRICT;

ALTER TABLE ONLY public."persona_cliente"
    ADD CONSTRAINT "persona_cliente_id_cliente_fkey" FOREIGN KEY (id_cliente) REFERENCES cliente_flowforest(id_cliente) ON DELETE CASCADE;

ALTER TABLE ONLY public."risorsa_umana"
    ADD CONSTRAINT "risorsa_umana_codice_fiscale_fkey" FOREIGN KEY (codice_fiscale) REFERENCES persona(codice_fiscale) ON DELETE RESTRICT;

ALTER TABLE ONLY public."struttura"
    ADD CONSTRAINT "struttura_nome_area_fkey" FOREIGN KEY (nome_area) REFERENCES area(nome) ON DELETE RESTRICT;

CREATE INDEX idx_biglietto_evento ON public.biglietto_persona USING btree (id_evento);

CREATE INDEX idx_biglietto_persona ON public.biglietto_persona USING btree (codice_fiscale);

CREATE INDEX idx_dettaglio_ordine_articolo ON public.dettaglio_ordine USING btree (codice_articolo);

CREATE INDEX idx_evento_data_inizio ON public.evento USING btree (data_inizio);

CREATE INDEX idx_evento_area_nome ON public.evento_area USING btree (nome_area);

CREATE INDEX idx_evento_partner_partner ON public.evento_partner USING btree (id_partner);

CREATE INDEX idx_feedback_data_compilazione ON public.feedback USING btree (data_compilazione);

CREATE INDEX idx_impiego_materiale_articolo ON public.impiego_materiale USING btree (codice_articolo);

CREATE INDEX idx_laboratorio_modulo_modulo ON public.laboratorio_modulo USING btree (id_modulo);

CREATE INDEX idx_ordine_data_ordine ON public.ordine USING btree (data_ordine);

COMMIT;
