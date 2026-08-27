# Manual de usuario de Cabildo

**Para el equipo de campana que no es gente de tecnologia.** No necesitas saber programar.
Solo necesitas saber que botones apretar y que reglas seguir.

---

## Que hace Cabildo

Cabildo es tu asistente de campana con IA. Se encarga de las partes aburridas y
que consumen mucho tiempo de una campana local, para que puedas dedicar tu tiempo
a hablar con los votantes.

- **Resumen matutino**: Que necesita pasar hoy
- **Borradores para redes sociales**: Publicaciones en TU voz, listas para tu aprobacion
- **Vigilancia del oponente**: Alertas cuando tu oponente hace algo publicamente
- **Listas de recorrido**: A quien visitar, que decir
- **Recaudacion de fondos**: A quien llamar, cuanto pedir
- **Monitoreo de noticias**: Que esta pasando en el distrito que deberias saber
- **Cumplimiento legal**: Fechas limite de reportes para que nunca se te pase una

## La regla mas importante

**Nada llega a un votante sin tu aprobacion.** Cabildo redacta borradores.
Tu los revisas. Tu los apruebas. Y entonces salen. Nunca al reves.

Cada pieza de contenido generado con IA incluye una nota: "[AI-assisted draft]".
Esto es ley en California y es lo correcto. No la quites.

---

## Como empezar

### Paso 1: Dale tu voz

Cabildo escribe mejor cuando sabe como escribes TU. Junta:
- Tus ultimas 10-20 publicaciones de Facebook
- Cualquier declaracion del concejo o comunicado de prensa
- Discursos o comentarios publicos

Guardalos en un archivo de texto (una publicacion por parrafo) y cargalos:
```
Copia tus publicaciones anteriores en un archivo llamado "my_posts.txt"
La IA aprendera tu estilo de escritura a partir de estos ejemplos.
```

### Paso 2: Conecta tus datos

Vas a necesitar esto (tu tesorero de campana o contacto del partido te puede ayudar):
- **NationBuilder** login (lo tienes a traves del patrocinio del partido Democrata)
- **FEC API key** -- gratis en api.data.gov, toma 2 minutos
- El nombre de tu oponente y cualquier cuenta publica de redes sociales que tenga

### Paso 3: Rutina diaria

**Cada manana:**
1. Revisa el resumen -- que se debe hoy, que paso durante la noche
2. Revisa los borradores de redes sociales -- aprueba, edita o rechaza
3. Revisa la vigilancia del oponente -- algo que necesite respuesta?
4. Agarra la lista de recorrido del dia si vas a tocar puertas

**Cada semana:**
1. Revisa la lista de llamadas para recaudacion -- haz 5-10 llamadas
2. Revisa las fechas limite de reportes -- algo proximo?
3. Revisa tus numeros de puertas tocadas -- vas al ritmo?

**Cada vez que regresas de tocar puertas:**
1. Registra las puertas que tocaste y cualquier nota
2. Marca los votantes que quieren seguimiento

---

## Lo que la IA NO va a hacer

- Publicar nada sin tu autorizacion
- Hacerse pasar por ti en ninguna comunicacion
- Acceder a informacion privada de nadie
- Segmentar votantes por raza, religion u otras caracteristicas protegidas
- Generar contenido que desaliente a la gente de votar
- Hackear nada ni acceder a datos no publicos

---

## Guia de modulos

### Resumen matutino
Tu tablero diario. Muestra: dias hasta la eleccion, puertas tocadas vs. la meta,
fechas limite proximas, actividad del oponente, contenido pendiente de revision.

### Redes sociales (Facebook)
Redacta publicaciones basadas en tu plataforma, tu voz y los eventos actuales. Cada
borrador incluye una nota de IA y necesita tu aprobacion antes de publicarse. Usa las
plantillas para tipos comunes de publicaciones: actualizaciones de canvassing, posiciones
sobre temas, eventos, endorsements, GOTV (movilizacion del voto).

### Vigilancia del oponente
Monitorea las redes sociales publicas de tu oponente y sus menciones en noticias. Cuando
publican algo o reciben cobertura de prensa, Cabildo redacta una respuesta enfocada en
los temas, no en ataques personales. Tu decides si la usas.

### Canvassing
Genera listas de recorrido a partir de tu archivo de votantes (NationBuilder/PDI) y
guiones para tocar puertas adaptados a los temas que estas escuchando. Registra
a quien has contactado y que dijeron.

### Recaudacion de fondos
Clasifica a los posibles donantes por probabilidad de donar y sugiere montos de
solicitud basados en su historial de donaciones (de datos publicos de FEC). Genera
una lista priorizada de llamadas.

### Noticias y sentimiento
Escanea noticias locales buscando historias relevantes a tu campana -- tu nombre,
el nombre de tu oponente, tus temas clave. Te alerta cuando algo esta siendo tendencia
para que puedas adelantarte.

### Cumplimiento legal
Rastrea las fechas limite de reportes de financiamiento de campana en California y revisa
todo el contenido generado por IA para detectar problemas de cumplimiento (nota de IA
faltante, suplantacion de identidad, lenguaje de supresion del voto).

---

## Consejos para mejores resultados

1. **Dale mas de tu escritura.** Mientras mas tenga, mejor suena como tu.
   Comentarios en reuniones del concejo, articulos de boletin, incluso
   comentarios largos de Facebook -- todo sirve.

2. **Edita los borradores, no solo los apruebes.** Agrega detalles personales,
   el nombre de un vecino, algo especifico del dia. La IA te da la estructura;
   tu le pones el alma.

3. **Registra tus notas de canvassing.** El sistema se vuelve mas inteligente sobre
   que temas enfatizar cuando sabe lo que los votantes realmente estan diciendo.

4. **Revisa la vigilancia del oponente todos los dias.** La velocidad importa en
   respuesta rapida. Una respuesta el mismo dia a una mala declaracion del oponente
   vale 10 veces mas que una respuesta tres dias despues.

5. **No publiques de mas.** 3-4 publicaciones de calidad por semana le ganan al
   ruido diario. La IA te redacta todo lo que quieras, pero tu audiencia tiene limites.

---

## Necesitas ayuda?

Esta herramienta fue construida por voluntarios que creen en la democracia local.
Si algo se rompe o necesitas ayuda, comunicate con tu contacto de tecnologia
de campana.

---

*Hecho con Cabildo -- herramientas de campana gratuitas y de codigo abierto para el resto de nosotros.*
