with staging as (
    select * from {{ ref('stg_crypto') }}
),

calculos_ventana as (
    select
        id,
        symbol,
        name,
        current_price,
        market_cap,
        total_volume,
        price_change_percentage_24h,
        ath,
        ath_change_percentage,
        extracted_at,
        
        -- Separamos el ranking por cada bloque de tiempo descargado
        rank() over (
            partition by extracted_at 
            order by market_cap desc
        ) as ranking_liquidez,
        
        -- CORREGIDO: Dividimos usando el campo extraído exacto (extracted_at)
        (market_cap / nullif(sum(market_cap) over (partition by extracted_at), 0)) * 100 as market_share_global,
        
        -- Clasificación de sentimiento de mercado según su variación de 24h
        case 
            when price_change_percentage_24h > 1.5 then 'Alcista'
            when price_change_percentage_24h < -1.5 then 'Bajista'
            else 'Estable'
        end as comportamiento_mercado
    from staging
)

select * from calculos_ventana
