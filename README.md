# Terradata

## Descripción

Terradata es una plataforma que proporciona una aplicación web intuitiva y accesible para permitir a los usuarios clasificar y analizar el tipo de superficie de una región seleccionada. Está diseñada para ayudar a profesionales en diversas tareas, tales como:

- Identificación y delimitación de áreas cultivables, brindando información relevante para la planificación y gestión de cultivos.
- Facilitar el trabajo de inteligencia territorial para el personal de organismos públicos, proporcionando herramientas de análisis geoespacial para la toma de decisiones informadas.
- Ofrecer informes detallados que permitan una interpretación fácil y rápida de la composición actual de una determinada región, brindando información valiosa para la planificación y la toma de decisiones.
- Implementar algoritmos de segmentación de imágenes satelitales para detectar y clasificar áreas construidas, permitiendo una identificación diferenciada de las superficies correspondientes a construcciones en la región seleccionada.

## Requisitos
Para instalar y ejecutar la plataforma de Terradata, es necesario tener instalado [Docker](https://www.docker.com/) y [Docker Compose](https://docs.docker.com/compose/).

## Instalación
- Clonar el repositorio de Terradata en tu máquina local.
- Navegar al directorio raíz del proyecto.
- Ejecutar el siguiente comando en la terminal para iniciar la aplicación:

```
docker-compose up -d
```

Al cabo de unos minutos, la aplicación se desplegará en los siguientes puertos:

#### Frontend: http://localhost:3000/
#### Backend: http://localhost:8000/admin

## Superusuario

Un superusuario está preconfigurado para acceder a la plataforma y al sitio de administración:

- Correo Electrónico: terradatademo@gmail.com
- Contraseña: Terre839ouasM

Este superusuario también se utiliza para acceder a la cuenta de correo electrónico donde se recibirán los reportes de las ejecuciones.


## Recomendaciones

Para obtener  mejores resultados en los procesos de segmentación y detección, se recomienda seleccionar el área con el máximo nivel de zoom posible. Esto proporciona una mayor resolución y detalle, lo que mejora la precisión de los algoritmos.

Por otro lado, para los cálculos de índices, se sugiere estar en un nivel de zoom sobre el mapa como se puede apreciar en los videos que se adjuntan con los respectivos ejemplos. Esto garantiza un equilibrio entre la resolución y la cobertura del área seleccionada, lo que es crucial para obtener mediciones precisas.


## Requisitos de Hardware

Antes de proceder con la instalación del proyecto, asegúrese de que su sistema cumpla con los siguientes requisitos de hardware:

- **Memoria RAM:** Mínimo 18 GB de RAM.
- **Almacenamiento:** Mínimo 20 GB de espacio disponible en disco.
