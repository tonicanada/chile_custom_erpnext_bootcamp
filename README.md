# Chile Custom

Personalización local para Chile sobre Frappe / ERPNext. Incluye validaciones de RUT, campos personalizados por DocType, helpers de región/comuna y endpoints API.

**Stack:** Frappe / ERPNext (bench)

## Qué incluye

- Validaciones y normalización de RUT para `Supplier`, `Customer`, `Employee` y `Shareholder`.
- Campos personalizados para Address, Project, Employee, Shareholder, Bank, Warehouse, Location y Expense Claim Detail.
- Helpers de regiones y comunas de Chile.
- Scripts de cliente para autocompletar región según comuna en Address y Project.
- Endpoints API para regiones y reportes de Purchase Invoice.

## Validaciones

- `tax_id` en `Supplier` y `Customer`.
- `rut` en `Employee` y `Shareholder`.

## Custom Fields

- `Address`: comuna, región, código de región.
- `Project`: prefijo, lat/long, URL Google Maps, país, comuna, región y dirección.
- `Employee`: RUT.
- `Shareholder`: RUT y tipo de accionista.
- `Bank`: código SBIF/CMF.
- `Warehouse`: proyecto asociado.
- `Location`: proyecto asociado (campo `linked_project`).
- `Expense Claim Detail`: tipo de comprobante, número de documento y proveedor.

## Client Scripts

- `Address`: al seleccionar comuna, completa región y código de región.
- `Project`: al seleccionar comuna, completa región.

## API

- `chile_custom.api.get_region_from_comuna(comuna)`
- `chile_custom.api.top_proveedores_pinv()`
- `chile_custom.api.facturas_pinv_por_fecha(fecha_inicio, fecha_fin, supplier=None)`

## Instalación

Puedes instalar esta app usando la CLI de bench:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app chile_custom
```

Luego ejecuta:

```bash
bench --site $SITE_NAME migrate
```

## Desarrollo

Esta app usa `pre-commit` para formato y linting. Instálalo y habilítalo así:

```bash
cd apps/chile_custom
pre-commit install
```

Herramientas configuradas:

- ruff
- eslint
- prettier
- pyupgrade

## Licencia

MIT
