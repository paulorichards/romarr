# La rama `casa`

Fork de [BlizzHacker/romarr](https://github.com/BlizzHacker/romarr) para el NAS
de la casa. `casa` corre nuestros parches encima de un release de upstream.
Licencia MIT.

Los parches se escriben **para proponerlos a upstream**: en inglés, con tests,
sobre `main`. La rama `casa` es el atajo para correrlos ya.

| Rama | Qué es | Quién la mueve |
|---|---|---|
| `main` | espejo de `upstream/main` | nosotros, al sincronizar |
| `casa` | release de upstream + nuestros parches + `casa-build` | nosotros |
| `feat/*`, `fix/*` | un parche, nacido de `main`, PR-able a upstream | nosotros |

`.casa/base` dice sobre qué release de upstream está `casa`. Hoy **1.6.0**, no
el último: upstream publicó seis releases en tres días (ver el README del stack
en nas-gitops), así que el salto de versión se decide aparte del parche.

## Parches que corren hoy

| Parche | Por qué |
|---|---|
| ratio de carátula por plataforma | la grilla dibujaba todo en `3/4` con `background-size: cover`, así que una caja apaisada perdía los lados: `3 Ninjas Kick Back` se leía "NJAS / CK BACK". Medido en la biblioteca de casa: con una sola forma, el 41 % de 16.522 carátulas se recortaba 15 % o menos |

⚠️ Ese parche **necesita RomM 5.4.2 o el fork `paulorichards/romm`**: el ratio
sale de `/api/platforms`, y RomM no lo exponía (la columna existía desde su
migración 0027 y nunca llegó a la API). Con un RomM viejo el parche no rompe
nada, simplemente no hay ratio y la grilla queda como estaba.

## Imágenes

`ghcr.io/paulorichards/romarr:1.6.0-casa.N` — sólo amd64. El despliegue es a
mano desde `nas-gitops`.
