create table if not exists public.car_fine
(
    id                   serial
        constraint "PK_00bba7a33c3b18d4d5a932a8891"
            primary key,
    "pSeryNumber"        varchar                            not null,
    "pComment"           varchar,
    "pStatus"            integer                            not null,
    "pPlace"             varchar,
    "pDate"              varchar                            not null,
    "pLocation"          varchar                            not null,
    "pViolation"         integer                            not null,
    "pAmount"            numeric                            not null,
    "pRemains"           numeric,
    "pMailDeliveredData" varchar,
    "pPaid"              numeric,
    "pPlateNumber"       varchar                            not null,
    "pDecreeDate"        varchar                            not null,
    "pInvoiceNumber"     varchar,
    "pURL"               varchar,
    privil               integer,
    "texpNumber"         varchar,
    "carId"              varchar,
    "LicensePhotoUrl"    varchar,
    "VehicleUrl"         varchar,
    "VideoUrl"           varchar,
    "DiscountStartDate"  varchar,
    source               car_fine_source_enum default 'telecom-soft'::car_fine_source_enum,
    "pMIB"               varchar,
    "pVideo"             varchar,
    "pPlateNumberImage"  varchar,
    "pPlateNumberAndCar" varchar,
    "createdAt"          timestamp            default now() not null,
    "updatedAt"          timestamp            default now() not null,
    "rawData"            json,
    "docIdTelecomSoft"   varchar
);

alter table public.car_fine
    owner to saferoad;

create index if not exists "IDX_b57b4d0218e561b598e54ee2d7"
    on public.car_fine ("pSeryNumber");

create index if not exists "IDX_66442313c5f005ccbb538e5016"
    on public.car_fine ("texpNumber");

create index if not exists "IDX_b39e239584ec1a38dc7c1b47bb"
    on public.car_fine ("carId");

