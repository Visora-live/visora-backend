-- Created by Redgate Data Modeler (https://datamodeler.redgate-platform.com)
-- Last modification date: 2026-05-25 02:01:07.394

-- tables
-- Table: camara
CREATE TABLE camara (
    id int  NOT NULL,
    nombre_cam varchar(50)  NOT NULL,
    direccion_ip varchar(15)  NOT NULL,
    puerto int  NOT NULL,
    ubicacion_camara varchar(50)  NOT NULL,
    estado boolean  NOT NULL,
    tienda_id int  NOT NULL,
    CONSTRAINT camara_pk PRIMARY KEY (id)
);

-- Table: evento
CREATE TABLE evento (
    id int  NOT NULL,
    estado varchar(20)  NOT NULL,
    fecha_hora timestamp  NOT NULL,
    comentario varchar(100)  NOT NULL,
    camara_id int  NOT NULL,
    CONSTRAINT evento_pk PRIMARY KEY (id)
);

-- Table: evento_imagen
CREATE TABLE evento_imagen (
    id int  NOT NULL,
    storage_ref varchar(50)  NOT NULL,
    evento_id int  NOT NULL,
    es_frame_representativo boolean  NOT NULL,
    confianza_arma decimal(5,4)  NOT NULL,
    confianza_rostro decimal(5,4)  NOT NULL,
    CONSTRAINT evento_imagen_pk PRIMARY KEY (id)
);

-- Table: identificacion
CREATE TABLE identificacion (
    id int  NOT NULL,
    nombre varchar(50)  NOT NULL,
    apellido varchar(50)  NOT NULL,
    dni varchar(8)  NOT NULL,
    evento_imagen_id int  NOT NULL,
    confianza_identificacion decimal(5,4)  NOT NULL,
    CONSTRAINT identificacion_pk PRIMARY KEY (id)
);

-- Table: rol
CREATE TABLE rol (
    id int  NOT NULL,
    tipo varchar(20)  NOT NULL,
    CONSTRAINT rol_pk PRIMARY KEY (id)
);

-- Table: tienda
CREATE TABLE tienda (
    id int  NOT NULL,
    nombre varchar(50)  NOT NULL,
    direccion varchar(50)  NOT NULL,
    RUC varchar(11)  NOT NULL,
    estado_tienda boolean  NOT NULL,
    licencia_inicio date  NOT NULL,
    licencia_fin date  NOT NULL,
    CONSTRAINT tienda_pk PRIMARY KEY (id)
);

-- Table: tienda_usuario
CREATE TABLE tienda_usuario (
    tienda_id int  NOT NULL,
    usuario_id int  NOT NULL,
    CONSTRAINT tienda_usuario_pk PRIMARY KEY (tienda_id,usuario_id)
);

-- Table: usuario
CREATE TABLE usuario (
    id int  NOT NULL,
    estado_acceso boolean  NOT NULL,
    username varchar(50)  NOT NULL,
    contrasena varchar(255)  NOT NULL,
    rol_id int  NOT NULL,
    CONSTRAINT usuario_pk PRIMARY KEY (id)
);

-- foreign keys
-- Reference: Evento_camera (table: evento)
ALTER TABLE evento ADD CONSTRAINT Evento_camera
    FOREIGN KEY (camara_id)
    REFERENCES camara (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Identificacion_Evento_imagen (table: identificacion)
ALTER TABLE identificacion ADD CONSTRAINT Identificacion_Evento_imagen
    FOREIGN KEY (evento_imagen_id)
    REFERENCES evento_imagen (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Imagen_Evento (table: evento_imagen)
ALTER TABLE evento_imagen ADD CONSTRAINT Imagen_Evento
    FOREIGN KEY (evento_id)
    REFERENCES evento (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Table_13_Tienda (table: tienda_usuario)
ALTER TABLE tienda_usuario ADD CONSTRAINT Table_13_Tienda
    FOREIGN KEY (tienda_id)
    REFERENCES tienda (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Table_13_Usuario (table: tienda_usuario)
ALTER TABLE tienda_usuario ADD CONSTRAINT Table_13_Usuario
    FOREIGN KEY (usuario_id)
    REFERENCES usuario (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Usuario_Rol (table: usuario)
ALTER TABLE usuario ADD CONSTRAINT Usuario_Rol
    FOREIGN KEY (rol_id)
    REFERENCES rol (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: camera_Tienda (table: camara)
ALTER TABLE camara ADD CONSTRAINT camera_Tienda
    FOREIGN KEY (tienda_id)
    REFERENCES tienda (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- End of file.

