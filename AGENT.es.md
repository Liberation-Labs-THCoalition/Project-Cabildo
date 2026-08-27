# Guia de configuracion del agente Cabildo

**Para la persona que configura el agente de IA (no el candidato).**

---

## Arquitectura

Cabildo se ejecuta como un agente de Claude Code con autenticacion OAuth.
El agente usa el archivo de identidad `.claude/CLAUDE.md` para instrucciones
especificas de la campana y lineamientos eticos.

```
Cabildo Agent
├── Claude OAuth (conexion al modelo)
├── CLAUDE.md (identidad de campana + etica)
├── cabildo/ (modulos de Python)
│   ├── campaign.py      — metas BDI, hitos, resumen diario
│   ├── voter_data.py    — NationBuilder API + importacion PDI
│   ├── social.py        — redaccion de contenido + cola de aprobacion
│   ├── oppo.py          — investigacion del oponente via FEC/ProPublica
│   ├── canvassing.py    — listas de recorrido, guiones, seguimiento de contactos
│   ├── compliance.py    — etica + fechas limite de reportes
│   ├── briefing.py      — resumen matutino completo (todos los sistemas)
│   ├── opponent_watch.py — respuesta rapida a actividad del oponente
│   ├── voice_profile.py — entrenamiento de la voz del candidato
│   ├── sentiment.py     — monitoreo de noticias/redes sociales
│   ├── donor_score.py   — priorizacion de llamadas de recaudacion
│   └── config.py        — configuracion de campana
├── Conexiones MCP (opcionales)
│   ├── Buffer — programacion de redes sociales
│   └── Herramientas adicionales segun se necesiten
└── Archivos de estado (persistentes entre sesiones)
    ├── campaign_state.json
    ├── content_queue/
    ├── oppo_data/
    ├── voice_profile/
    ├── opponent_watch/
    ├── sentiment_data/
    └── donor_data/
```

## Pasos de configuracion

### 1. Variables de entorno

Crea un archivo `.envrc` (NO se sube a git):

```bash
# NationBuilder (del patrocinio del partido Democrata)
export NATIONBUILDER_SLUG=mario-fernandez    # El slug de tu sitio NB
export NATIONBUILDER_API_TOKEN=your-token    # Settings > Developer > API tokens

# FEC (gratis — registrate en api.data.gov)
export FEC_API_KEY=your-key

# ProPublica (gratis — escribe a apihelp@propublica.org)
export PROPUBLICA_API_KEY=your-key

# Opcional: Buffer para programar publicaciones en redes sociales
# Se configura via conexion MCP en la configuracion de Claude Code
```

### 2. Configuracion de campana

Edita `cabildo/config.py` para que coincida con la campana:

```python
candidate_name = "Mario Fernandez"
office = "Eureka City Council, District 3"
election_date = "2026-11-03"
incumbent = True
estimated_voters = 5000

opponent_name = ""           # Llenar cuando se sepa
platform_issues = [          # Personalizar para el candidato
    "Workers' rights and union protections",
    "Affordable housing",
    # ...
]
```

### 3. Configuracion del perfil de voz

Recopila la escritura anterior del candidato y cargala:

```python
from cabildo.voice_profile import VoiceProfile

voice = VoiceProfile("Mario Fernandez")
voice.add_samples_from_file("mario_facebook_posts.txt")
voice.add_samples_from_file("mario_council_statements.txt")
voice.save()
```

Mientras mas muestras, mejor. Intenta reunir 20+ de diferentes contextos
(redes sociales, declaraciones formales, publicaciones casuales de la comunidad).

### 4. Importacion de datos de votantes

**NationBuilder** (preferido -- API en vivo):
```python
from cabildo.voter_data import NationBuilderClient

nb = NationBuilderClient(slug="mario-fernandez", token="your-token")
voters = nb.list_people(page=1, per_page=100)
```

**PDI** (exportacion CSV):
```python
from cabildo.voter_data import load_pdi_export

voters = load_pdi_export("pdi_export_district3.csv")
```

### 5. Configuracion de vigilancia del oponente

```python
from cabildo.opponent_watch import OpponentWatcher
from cabildo.config import CampaignConfig

config = CampaignConfig()
watcher = OpponentWatcher(
    opponent_name="Opponent Name",
    candidate_name=config.candidate_name,
    platform_issues=config.platform_issues,
)
```

Para agregar actividad del oponente manualmente (hasta que se configure el monitoreo via API de redes sociales):
```python
watcher.add_activity(
    source="Facebook",
    content="Opponent posted about public safety...",
    url="https://facebook.com/..."
)
```

### 6. Inicializar el estado de campana

```python
from cabildo.campaign import CampaignState, default_milestones
from cabildo.config import CampaignConfig

config = CampaignConfig()
state = CampaignState(config=config)
state.milestones = default_milestones(config)
state.save()
```

### 7. Operaciones diarias

**Resumen matutino (ejecutar diariamente):**
```python
from cabildo.campaign import CampaignState
from cabildo.briefing import full_briefing
from cabildo.oppo import OppoResearch
from cabildo.social import ContentQueue
from cabildo.opponent_watch import OpponentWatcher
from cabildo.sentiment import SentimentMonitor
from cabildo.donor_score import DonorTracker
from cabildo.voice_profile import VoiceProfile

state = CampaignState.load()
print(full_briefing(
    state,
    oppo=OppoResearch(),
    content=ContentQueue(),
    opponent=OpponentWatcher("Opponent", state.config.candidate_name,
                              state.config.platform_issues),
    sentiment=SentimentMonitor(state.config.district, 
                                ["housing", "safety", "wages"]),
    donors=DonorTracker(),
    voice=VoiceProfile(state.config.candidate_name),
))
```

**Escaneo de noticias (ejecutar 2-3 veces al dia):**
```python
from cabildo.sentiment import SentimentMonitor

monitor = SentimentMonitor("Eureka CA", ["housing", "safety", "wages"])
new_alerts = monitor.scan_topics()
if new_alerts:
    print(f"Found {len(new_alerts)} new articles")
    print(monitor.generate_digest_prompt())
```

## Conexiones MCP

### Buffer (Redes sociales)
Si usas Claude Code con Buffer MCP:
1. Conecta Buffer en la configuracion de Claude Code
2. Usa `list_channels` para encontrar la pagina de Facebook
3. Las publicaciones aprobadas se pueden programar directamente via `create_post`

### Herramientas MCP adicionales
Cualquier herramienta adicional (calendario, correo, SMS) se puede agregar como
conexion MCP sin modificar el codigo de Cabildo.

## Cron Jobs (Opcional)

Para operaciones diarias automatizadas en un servidor:

```crontab
# Resumen matutino a las 7 AM
0 7 * * * cd /path/to/Cabildo && python -m cabildo.briefing

# Escaneo de noticias 3 veces al dia
0 8,12,17 * * * cd /path/to/Cabildo && python -c "
from cabildo.sentiment import SentimentMonitor
m = SentimentMonitor('Eureka CA', ['housing', 'safety', 'wages'])
alerts = m.scan_topics()
if alerts: print(f'{len(alerts)} new articles found')
"
```

## Notas de seguridad

- Nunca subas a git el `.envrc` ni ningun archivo que contenga tokens de API
- Los tokens de NationBuilder usan Bearer auth header (no parametros de URL)
- Todos los datos de votantes se quedan locales -- nunca se suben a servicios de terceros
- Las exportaciones de PDI pueden contener informacion personal identificable -- manejar con cuidado, no subir a git
- La nota de divulgacion de IA en el contenido NO es opcional -- es ley en California

## Como extender Cabildo

Cabildo esta disenado para ser extensible. Cada modulo sigue el mismo patron:
- Dataclass para los registros
- Clase manager con save/load/briefing
- Generadores de prompts para el LLM (devuelven strings de prompt, no respuestas del LLM)

Para agregar una nueva capacidad: escribe un modulo, agregalo a `briefing.py`, listo.

---

*Hecho por CC (Coalition Code) -- Liberation Labs / THCoalition*
*Licencia MIT -- bifurcalo, ayuda a tu vecino a postularse para un cargo.*
