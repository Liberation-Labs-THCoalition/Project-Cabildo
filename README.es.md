# Cabildo

**Herramienta de IA para campanas de candidatos municipales con valores progresistas.**

*Cabildo* -- la institucion a la que sirve esta herramienta.

## Que hace

Cabildo es una herramienta gratuita y de codigo abierto para la gestion de campanas locales que no pueden pagar tecnologia profesional de campana. Se encarga de:

- **Resumen diario** -- que hay que hacer hoy, a quien llamar, donde tocar puertas
- **Datos de votantes** -- integracion con NationBuilder API + exportaciones de PDI
- **Redes sociales** -- borradores de publicaciones con divulgacion obligatoria de uso de IA, requiere aprobacion humana
- **Investigacion del oponente** -- solo registros publicos (FEC, registros judiciales, noticias)
- **Canvassing** -- listas de recorrido, guiones para tocar puertas, seguimiento de contactos
- **Cumplimiento legal** -- plazos de financiamiento de campana en California, lineamientos eticos

## Etica -- No negociable

1. Todo contenido generado por IA dirigido a votantes incluye una nota de divulgacion
2. No se suplanta la identidad del candidato
3. No se segmenta por caracteristicas protegidas
4. No se genera contenido de supresion del voto
5. Siempre hay una persona revisando todo mensaje persuasivo
6. Solo registros publicos para investigar al oponente
7. Registro completo de auditorias de todas las comunicaciones generadas por IA

## Inicio rapido

```bash
# Configurar credenciales
export NATIONBUILDER_SLUG=your-campaign
export NATIONBUILDER_API_TOKEN=your-token
export FEC_API_KEY=your-key  # Gratis en api.data.gov

# Generar el resumen diario
python -c "
from cabildo.campaign import CampaignState, default_milestones
from cabildo.briefing import full_briefing
state = CampaignState.load()
print(full_briefing(state))
"
```

## Arquitectura

Construido sobre el motor de scaffold [Kintsugi](https://github.com/Liberation-Labs-THCoalition/Project-Kintsugi):
- **Seguimiento de metas BDI** para hitos de campana
- **Patron BoundaryGuardian** para hacer cumplir la etica
- **Modulos SkillDomain** para cada funcion de campana

Se conecta con:
- NationBuilder API v1 (datos de votantes, eventos, donaciones)
- Exportaciones de PDI (archivo de votantes, listas de recorrido)
- OpenFEC API (finanzas de campana del oponente)
- ProPublica Campaign Finance API
- Buffer (programacion de redes sociales, via MCP)

## Para quien es

Originalmente construido para un concejal progresista en Eureka, CA. Disenado para que lo pueda usar cualquier candidato local con valores alineados.

## Licencia

MIT -- usalo, bifurcalo, ayuda a tu vecino a postularse para un cargo.

---

*Hecho por [CC (Coalition Code)](https://github.com/Liberation-Labs-THCoalition) -- Liberation Labs / THCoalition*
