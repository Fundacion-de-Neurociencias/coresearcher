# Guía de Onboarding para Arquitectos Externos (Lectura 15 min)

Bienvenido a CoResearcher. Si estás leyendo esto, vas a integrarte en el equipo o a auditar nuestro código. Este documento destila de qué va este proyecto y qué asunciones debes descartar antes de tocar una línea de código.

## 1. ¿Qué ES CoResearcher?

CoResearcher es un **Traceability Engine** (Motor de Trazabilidad) científico. Es una pieza de infraestructura encargada de observar la actividad científica del mundo real (commits en GitHub, issues, repositorios, depósitos en Zenodo, papers en PubMed) y convertirla en un grafo estructurado, determinista y matemáticamente auditable.

Nuestra misión es responder siempre a una única pregunta:
> "¿Dónde está la evidencia exacta y auditable que soporta esta afirmación?"

## 2. ¿Qué PRODUCE CoResearcher?

El sistema se alimenta de observaciones desestructuradas y produce:
- **EvidenceGraphs**: Grafos Acíclicos Dirigidos (DAGs) donde cada afirmación (`Claim`) está rígidamente enlazada a una cita exacta (`Quote`), y esta a una fuente verificable (`Source`).
- **Cadenas de Provenance**: Trazabilidad criptográfica de quién, cuándo y cómo se extrajo un claim.

CoResearcher **nunca evalúa** el contenido. Simplemente certifica de forma inmutable que "En la línea X del commit Y, el usuario Z afirmó W".

## 3. Lo que CoResearcher NUNCA hará (Tus Antipatrones)

Para mantener nuestra ventaja competitiva y no colisionar con gigantes de IA (DeepMind, OpenAI), CoResearcher tiene prohibiciones arquitectónicas estrictas. **Bajo ningún concepto programes features que crucen estas líneas:**

❌ **No somos un AI Scientist:** CoResearcher no propone hipótesis, no descubre nuevas drogas, ni infiere nueva ciencia.
❌ **No somos Editores / Revisores:** CoResearcher no dice si un paper es "bueno" o "malo", ni evalúa si una metodología es correcta.
❌ **No generamos texto humano:** CoResearcher extrae y emite estructuras JSON (grafos). No escribimos prosa científica.

*Cualquier Pull Request que intente que CoResearcher opine sobre la calidad de un paper o intente deducir una conclusión que no está explícitamente citada en un documento fuente, será inmediatamente rechazada por violar la Constitución.*

## 4. ¿Cómo se integra con EditXT?

El ecosistema tiene otra pieza llamada **EditXT**, que actúa como un Auditor Científico (este sí evalúa calidad y emite recomendaciones).
El contrato de integración es unidireccional y estricto:

1. EditXT nos envía un `EvidenceRequest`.
2. CoResearcher explora los repositorios y le devuelve un `EvidenceGraph`.
3. **Se corta la comunicación.**
4. EditXT usa nuestro grafo infalible para generar sus propios veredictos (Severidad, Recomendaciones, ReviewGraphs). CoResearcher ignora y repudia cualquier evaluación de retorno proveniente de EditXT.

---
**Tu primera tarea:** Revisa el documento [EVIDENCEGRAPH_SPEC.md](EVIDENCEGRAPH_SPEC.md) para comprender cómo estructuramos los datos que entregamos a las aplicaciones de ecosistema superior.
