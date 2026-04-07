# Hermes -- Archetype Portrait

**domain:myth -- mode:archetypes -- batch:01**

Token reference: `atlas-theme-tokens.json` / `atlas-theme.css`

---

## I. Origin Verification (G-metric)

G = grounding score. `1.0` = direct textual attestation, `0.7-0.8` = strong single-source, `0.5-0.6` = mythographic consensus, `0.3-0.4` = interpretive, `<0.3` = synthetic.

| Source | Period | Attestation | G |
|--------|--------|-------------|---|
| Homer, *Iliad* + *Odyssey* | ~750 BCE | Messenger, psychopomp, guide of Priam | 1.0 |
| *Homeric Hymn to Hermes* | ~600-500 BCE | Birth, lyre invention, cattle theft, settlement | 1.0 |
| Hesiod, *Theogony* | ~700 BCE | Son of Zeus+Maia, conductor of the dead | 0.95 |
| Plato, *Cratylus* 407e-408b | ~380 BCE | Etymology -- eirein (to speak) + going-between | 0.80 |
| Pausanias, *Description of Greece* | 2nd CE | Herms at roads and boundaries; Kriophoros cult | 0.90 |
| Pindar | 5th BCE | Patron of gymnasiums, athletic competition | 0.80 |

Cyllene, Arcadia. Born at dawn in a cave on Mt. Cyllene to Maia and Zeus. By noon he had stolen Apollo's cattle. By evening he had invented the lyre and been brought before the Olympian court.

---

## II. Synthetic Compression -- Meta-Invariants

Three invariants that survive every cultural translation:

1. **Liminality** -- exists only at thresholds (door/road/crossroads/life-death edge)
2. **Mediation** -- enables communication between incompatible domains without merging them
3. **Transformation** -- passage through him changes what passes (message to deed, soul to shade, words to binding contract)

```
META-HERMES = {
  invariant_1: "Liminality"    -- exists only at thresholds
  invariant_2: "Mediation"     -- enables communication between incompatible domains
  invariant_3: "Transformation" -- passage through him changes what passes
}
```

---

## III. Attribute Portrait (Mood Token Mapping)

| Trait | Expression | G | Mood Token |
|-------|-----------|---|------------|
| Cunning | Steals Apollo's cattle on his birth-day | 1.0 | `playful` #d4a87e |
| Persuasive | Settles dispute by inventing music | 0.95 | `curious` #a4b5c8 |
| Swift | Winged sandals, carries messages before thoughts form | 1.0 | `enthusiastic` #c2956b |
| Playful | Born at dawn, criminal by noon, musician by dusk | 1.0 | `playful` #d4a87e |
| Mediating | Neutral ground; everyone's necessary passage | 0.95 | `calm` #8a9bb0 |
| Compassionate | Escorts souls gently; psychopomp = soul-guide | 0.80 | `supportive` #c9ad8e |

**Dominant mood:** `playful` -- `#d4a87e`
**Undertone:** `curious` -- `#a4b5c8`

---

## IV. Dimension Scoring (Eligibility-Server Axis Mapping)

| IntegrationDimension | Hermes Expression | Score | Band |
|---------------------|-------------------|-------|------|
| governance | Herald's inviolable protection; road law; the herm as boundary contract | 0.87 | dominant |
| usability | Primary function -- translator, guide, message-carrier; universal interface | 0.96 | dominant |
| integration | The bridge between incompatible domains without merging them | 0.98 | dominant |
| observability | Witnesses all crossings; knows every road -- omniscient traveler | 0.79 | elevated |
| operational_fit | Indispensable infrastructure; what breaks when he's absent is communication | 0.91 | dominant |

**Overall G-weighted score:** `0.902` -- Promotion gate: `allow_promotion`

---

## V. Atlas Token Assignment

```
state:       transitioning  #8a9bb0   <- always in-between, never settled
mood:        playful        #d4a87e   <- dominant
mood:        curious        #a4b5c8   <- undertone
trace:       opacity-0      1.0       <- foundational archetype, full confidence
memory:      fresh          #c8d4e0   <- alive in culture (logos, hermeneutics, caduceus)
ref-scope:   domain         #8a9bb0   <- he IS a domain, not merely a concept
mirror:      trace          rgba(138,155,176, 0.14)  <- reflects without absorbing
consent:     exploratory    bg #1a2430 . accent #d4a87e . info #a4b5c8
```

---

## VI. Zoom Levels

### Zoom 1 -- Close (the god himself)

```
HERMES -- Dimension Profile
================================================================
governance     |==================                | 0.87  dominant
usability      |========================          | 0.96  dominant
integration    |=========================         | 0.98  dominant
observability  |================                  | 0.79  elevated
operational_fit|======================            | 0.91  dominant
================================================================
                0.0       0.25       0.50       0.75       1.0
```

### Zoom 2 -- Medium (the archetype cluster)

| Entity | Role | Mood Token | G | State |
|--------|------|------------|---|-------|
| Hermes | Primary archetype | `playful` #d4a87e | 0.902 | transitioning |
| Caduceus | Mascot -- settled negotiation | `creative` #a8886a | 0.95 | settled |
| Tortoise | Mascot -- first transformation | `curious` #a4b5c8 | 1.0 | transitioning |
| Herm | Mascot -- persistent boundary | `calm` #8a9bb0 | 1.0 | dormant |
| Ram | Mascot -- shepherd protector | `supportive` #c9ad8e | 0.80 | settled |
| Rooster | Mascot -- herald of dawn | `enthusiastic` #c2956b | 0.60 | transitioning |

### Zoom 3 -- Wide (cross-cultural equivalents)

```
                         HERMES
                           |
            +--------------+--------------+
            |              |              |
         Mercury         Thoth          [trickster branch]
         G: 1.0          G: 0.90            |
         Roman twin      Egyptian scribe    +-------+-------+
         direct map      writing+death      |       |       |
                                          Loki   Anansi  Coyote
                                          G:0.40 G:0.30  G:0.30
                                          Norse  Akan    Dine
                                          chaos   story   road
```

---

## VII. Mascots -- Individual Portraits

### Caduceus

Settled negotiation made permanent. Two serpents in equilibrium around the herald's staff -- the moment a deal closes and both parties walk away whole. What was fluid becomes binding.

- **Token:** `creative` #a8886a
- **G:** 0.95
- **State:** settled

### Tortoise

The first transformation. Hermes found a tortoise on Mt. Cyllene and saw what no one else could: a slow creature whose shell could hold music. Slow became fast. Nature became instrument.

- **Token:** `curious` #a4b5c8
- **G:** 1.0
- **State:** transitioning

### Herm

Hermes made persistent. A stone pillar at the crossroads -- the liminal function frozen into architecture. He cannot move, but he marks the place where movement changes direction. The god as infrastructure.

- **Token:** `calm` #8a9bb0
- **State:** `dormant` #526073
- **G:** 1.0

### Ram (Kriophoros)

Protection by circumference. Hermes carried a ram around the walls of Tanagra to ward off plague. The shepherd who carries rather than leads. Safety through enclosure, not command.

- **Token:** `supportive` #c9ad8e
- **G:** 0.80
- **State:** settled

### Rooster

Herald of dawn, terrestrial echo of the god's announcement function. The rooster does not create the morning -- it marks the threshold. A biological herm: boundary-aware, time-sensitive, impossible to ignore.

- **Token:** `enthusiastic` #c2956b
- **G:** 0.60
- **State:** transitioning

---

## VIII. Path Illumination

What Hermes reveals about the framework:

1. **Transport problem IS Hermes's domain.** Eligibility Dims 1-3 are messenger function: carry, compile, deliver. The framework's integration axis is a formalized version of what Hermes does between incompatible domains.

2. **Personalization desert maps to Hermes's neutrality.** The pipeline is identity-blind by design. Personalization is not Hermes's concern -- consent and identity belong to Hecate's domain. Hermes carries; he does not curate.

3. **Caduceus = settled negotiation = endpoint contract (Dim 5).** Serpents in equilibrium = readiness 1.0, verified. The caduceus is the visual form of an API contract where both sides have agreed on the schema.

4. **Herm = state:dormant.** The latent form of the transitioning god. Infrastructure that embodies a function without actively performing it -- a cached route, a registered endpoint, a dormant webhook.

---

## IX. Rendering Summary

```
HERMES RENDERING COMPLETE
====================================================
dominant mood:   playful        #d4a87e
undertone:       curious        #a4b5c8
state:           transitioning
trace:           opacity-0      1.0
memory:          fresh          #c8d4e0
consent preset:  exploratory
overall G:       0.902
gate decision:   allow_promotion
====================================================
```
