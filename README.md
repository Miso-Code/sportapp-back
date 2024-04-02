# SportApp

Repositorio para el Backend de la aplicación SportApp. Este es un monorepo que contiene todos los microservicios
necesarios para el correcto funcionamiento de la aplicación.

## Estructura del repositorio

El repositorio está dividido en las siguientes carpetas:

- `.github`
    - `workflows`: Contiene los workflows de GitHub Actions.
- `infra`
    - `terraform`: Contiene los archivos necesarios para desplegar la infraestructura en AWS.
        - `aws`: Contiene los archivos necesarios para desplegar la infraestructura en AWS.
            - `modules`: Contiene módulos de Terraform reutilizables.
            - `resources`: Contiene los recuros básicos de la infraestructura (VPC, subnets, DBs, etc.)
            - `services`: Contiene los servicios de AWS necesarios para la aplicación.
        - `gcp`: Contiene los archivos necesarios para desplegar la infraestructura en GCP.
            - `modules`: Contiene módulos de Terraform reutilizables.
            - `resources`: Contiene los recuros básicos de la infraestructura (VPC, subnets, DBs, etc.)
            - `services`: Contiene los servicios de GCP necesarios para la aplicación.
    - `scripts`: Contiene scripts para automatizar tareas de despliegue.
- `projects`: Contiene los microservicios de la aplicación.}
    - `<microservicio>`: Contiene el código fuente de un microservicio.
        - `app`: Contiene el código fuente del microservicio.
        - `tests`: Contiene los tests del microservicio.
- `shared`: Contiene código compartido entre los microserviacios.

## Herramientas necesarias

- [Terraform](https://www.terraform.io/): Herramienta para la creación y gestión de infraestructura como código.
- [Docker](https://www.docker.com/): Herramienta para la creación y gestión de contenedores.
- [Docker Compose](https://docs.docker.com/compose/): Herramienta para la definición y ejecución de aplicaciones Docker
  multi-contenedor.
- [Python](https://www.python.org/): Lenguaje de programación en el que están escritos los microservicios.
- [Poetry](https://python-poetry.org/): Herramienta para la gestión de dependencias de Python.
- [Make](https://www.gnu.org/software/make/): Herramienta para la automatización de tareas.

## Ejecución

### Local

Para ejecutar los microservicios en local, ejecutar el siguiente comando:

```bash
cd projects/<microservicio> && poetry run uvicorn app.main:app --reload
```

### Docker

Para ejecutar los microservicios en Docker, primero se debe construir la imagen de Docker. Para construir la imagen de
Docker, ejecutar el siguiente comando:

```bash
cd projects/<microservicio> && docker build -t sportapp/<microservicio> .
```

Para ejecutar la imagen de Docker, ejecutar el siguiente comando:

```bash
docker run -p 8000:8000 sportapp/<microservicio>
```

## Pruebas

Se realizan pruebas unitarias y de integración para los microservicios. Estas pruebas se realizan con Pytest.

Para ejecutar los tests de todos los microservicios, ejecutar el siguiente comando:

```bash
make test
```

Para ejecutar los tests de un microservicio en particular, ejecutar el siguiente comando:

```bash
cd projects/<microservicio> && poetry run pytest
```

## Nube

### AWS

AWS será el principal proveedor de servicios en la nube para la aplicación. En esta se desplegará la versión de
producción y desarrollo de la aplicación. Se utilizarán los siguientes servicios:

- ECS+Fargate: Para el despliegue de los microservicios.
- RDS: Para la base de datos (PostgreSQL).
- SQS: Para la cola de mensajes (mensajería asíncrona).
- Lambda: Para la ejecución de funciones serverless (Lambda Authorizer).
- API Gateway: Para la exposición de las APIs.
- Load Balancer: Para el balanceo de carga desde el API Gateway a los microservicios.

#### Despliegue de la infraestructura

Se utiliza Terraform para desplegar la infraestructura en AWS. Para desplegar la infraestructura, ejecutar los
siguientes comandos:

Para crear los recursos básicos de la infraestructura:

```bash
cd infra/terraform/aws/resources && terraform init && terraform apply
```

Para crear los servicios de la infraestructura:

```bash
cd infra/terraform/aws/services/<servicio> && terraform init && terraform apply
```

### GCP

GCP será el proveedor de servicios en la nube secundario para la aplicación. Su principal propósito es servir como una
ayuda para el Frontend de la aplicación ya que acá se desplegarán los servicios en su versión de prueba (features), así
se tendrá un feedback más rápido de los cambios realizados. Esta decisión se tomó para evitar que el Frontend tenga que
esperar a que se desplieguen los servicios en AWS, al igual que para aprovechar los créditos gratuitos de GCP. Se
utilizarán los siguientes servicios:

- Cloud Run: Para el despliegue de los microservicios.
- Cloud SQL: Para la base de datos (PostgreSQL).

#### Despliegue de la infraestructura

Se utiliza Terraform para desplegar la infraestructura en GCP. Para desplegar la infraestructura, ejecutar los
siguientes comandos:

Para crear los recursos básicos de la infraestructura:

```bash
cd infra/terraform/gcp/resources && terraform init && terraform apply
```

Para crear los servicios de la infraestructura:

```bash
cd infra/terraform/gcp/services && terraform init && terraform apply
```
