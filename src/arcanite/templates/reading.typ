// Arcanite Reading Report Template
// Renders tarot readings to PDF

// =============================================================================
// Page Setup
// =============================================================================

#set page(
  paper: "us-letter",
  margin: (x: 1in, y: 1in),
)

#set text(font: "Libertinus Serif", size: 11pt)
#set par(justify: true, leading: 0.65em)

// =============================================================================
// Variables (populated by Python)
// =============================================================================

#let reading_title = "READING_TITLE"
#let spread_name = "SPREAD_NAME"
#let reading_date = "READING_DATE"
#let question = none
#let question_type = none

// Cards array: ((name, position, orientation, image_path, interpretation, keywords, position_desc, archetype, core_essence, psychological, shadow, element, zodiac), ...)
#let cards = ()

// Relationships array: ((card1, card2, type, interpretation), ...)
#let relationships = ()

// The synthesized reading narrative
#let synthesis = []

// Layout positions for spread visualization
#let layout_positions = ()

// Config flags
#let show_spread_visual = true
#let show_card_images = true
#let show_relationships = true
#let show_synthesis = true  // Only show Reading section for LLM-synthesized readings
#let show_prompt_appendix = false  // Debug: show full LLM prompt

// Prompt content for appendix (when enabled)
#let system_prompt = none
#let user_prompt = none

// =============================================================================
// Colors
// =============================================================================

#let accent-color = rgb(74, 85, 104)
#let card-border = rgb(226, 232, 240)
#let card-bg = rgb(250, 250, 250)
#let upright-color = rgb(39, 103, 73)
#let reversed-color = rgb(155, 44, 44)
#let relationship-bg = rgb(255, 250, 240)
#let relationship-border = rgb(237, 137, 54)

// =============================================================================
// Helper Functions
// =============================================================================

#let section-heading(title) = {
  v(1em)
  line(length: 100%, stroke: 0.5pt + accent-color)
  v(0.3em)
  text(weight: "bold", size: 13pt, fill: accent-color)[#title]
  v(0.5em)
}

#let card-frame(content) = {
  block(
    width: 100%,
    inset: 12pt,
    radius: 4pt,
    stroke: 0.5pt + card-border,
    fill: card-bg,
    content
  )
}

#let keyword-tag(word) = {
  box(
    inset: (x: 6pt, y: 3pt),
    radius: 3pt,
    fill: rgb(226, 232, 240),
    text(size: 9pt, fill: accent-color)[#word]
  )
}

// =============================================================================
// Title Section
// =============================================================================

#align(center)[
  #text(size: 24pt, weight: "bold")[#reading_title]
  #v(0.5em)
  #text(size: 14pt, fill: gray)[#spread_name]
  #v(1em)
  #line(length: 40%, stroke: 1pt + accent-color)
  #v(1em)
]

#if question != none [
  #align(center)[
    #block(
      width: 80%,
      inset: 16pt,
      radius: 6pt,
      fill: rgb(247, 250, 252),
      stroke: 0.5pt + accent-color,
    )[
      #text(style: "italic", size: 12pt)[#question]
      #if question_type != none [
        #v(0.5em)
        #text(size: 10pt, fill: gray)[Focus: #question_type]
      ]
    ]
  ]
  #v(1em)
]

#text(size: 10pt, fill: gray)[Reading generated #reading_date]

// =============================================================================
// Spread Visualization
// =============================================================================

#if show_spread_visual and layout_positions.len() > 0 [
  #section-heading("Spread Layout")

  // Container dimensions
  #let container-width = 450pt
  #let container-height = 175pt
  #let card-width = 55pt
  #let card-height = 77pt

  #block(
    width: container-width,
    height: container-height,
    fill: rgb(248, 250, 252),
    radius: 8pt,
    stroke: 0.5pt + card-border,
  )[
    #for (i, pos) in layout_positions.enumerate() [
      // Convert percentage positions to actual coordinates
      // Center cards on their position by subtracting half card dimensions
      #let x-pos = (pos.at(0) / 100) * container-width - (card-width / 2)
      #let y-pos = (pos.at(1) / 100) * container-height - (card-height / 2)

      #place(
        dx: x-pos,
        dy: y-pos,
      )[
        #let card = cards.at(i, default: none)
        #if card != none [
          #let card-image-path = card.at(3)
          #let card-orientation = card.at(2)

          // Show card image if available, otherwise text fallback
          #if show_card_images and card-image-path != none and card-image-path != "none" [
            #stack(
              dir: ttb,
              spacing: 2pt,
              box(
                width: card-width,
                height: card-height,
                radius: 3pt,
                clip: true,
                stroke: 1pt + accent-color,
              )[
                #if card-orientation == "reversed" [
                  #rotate(180deg)[#image(card-image-path, width: 100%, height: 100%, fit: "cover")]
                ] else [
                  #image(card-image-path, width: 100%, height: 100%, fit: "cover")
                ]
              ],
              align(center)[#text(size: 6pt, fill: accent-color)[#card.at(1)]]
            )
          ] else [
            // Text fallback when no image
            #box(
              width: card-width,
              height: card-height,
              radius: 3pt,
              fill: white,
              stroke: 1pt + accent-color,
              inset: 4pt,
            )[
              #set text(hyphenate: true)
              #set par(justify: false, leading: 0.4em)
              #align(center + horizon)[
                #text(size: 7pt, weight: "bold")[#card.at(1)]
                #v(3pt)
                #text(size: 6pt)[#card.at(0)]
              ]
            ]
          ]
        ]
      ]
    ]
  ]
  #v(1em)
]

// =============================================================================
// Card-by-Card Interpretations
// =============================================================================

#section-heading("Cards Drawn")

#for (i, card) in cards.enumerate() [
  #let name = card.at(0)
  #let position = card.at(1)
  #let orientation = card.at(2)
  #let image_path = card.at(3)
  #let interpretation = card.at(4)
  #let keywords = card.at(5)
  #let position_desc = card.at(6)
  #let archetype = card.at(7, default: none)
  #let core_essence = card.at(8, default: none)
  #let psychological = card.at(9, default: none)
  #let shadow = card.at(10, default: none)
  #let element = card.at(11, default: none)
  #let zodiac = card.at(12, default: none)

  #let orient-color = if orientation == "reversed" { reversed-color } else { upright-color }

  #card-frame[
    #grid(
      columns: if show_card_images and image_path != none and image_path != "none" { (85pt, 1fr) } else { (1fr,) },
      gutter: 16pt,

      // Card image column (if enabled)
      if show_card_images and image_path != none and image_path != "none" [
        #box(
          width: 75pt,
          height: 110pt,
          radius: 4pt,
          clip: true,
          stroke: 0.5pt + card-border,
        )[
          #if orientation == "reversed" [
            #rotate(180deg)[#image(image_path, width: 100%, height: 100%, fit: "cover")]
          ] else [
            #image(image_path, width: 100%, height: 100%, fit: "cover")
          ]
        ]
      ],

      // Text content column
      [
        #text(size: 14pt, weight: "bold")[#name]
        #h(6pt)
        #text(size: 11pt, fill: orient-color)[(#orientation)]
        #if archetype != none and archetype != "" [
          #h(6pt)
          #text(size: 9pt, fill: gray, style: "italic")[#archetype]
        ]
        // Elemental correspondences (inline)
        #if element != none or zodiac != none [
          #h(6pt)
          #text(size: 9pt, fill: accent-color)[
            #if element != none [#element]
            #if element != none and zodiac != none [·]
            #if zodiac != none [#zodiac]
          ]
        ]
        #v(3pt)

        #text(size: 10pt, weight: "semibold", fill: accent-color)[#position]
        #if position_desc != none [
          #text(size: 10pt, fill: gray)[ — #position_desc]
        ]
        #v(5pt)

        // Core essence
        #if core_essence != none and core_essence != "" [
          #text(size: 10pt, style: "italic", fill: rgb(100, 100, 100))[#core_essence]
          #v(5pt)
        ]

        #text(size: 11pt)[#interpretation]

        #if keywords.len() > 0 [
          #v(5pt)
          #for word in keywords [
            #keyword-tag(word)
            #h(3pt)
          ]
        ]

        // Psychological dimension
        #if psychological != none and psychological != "" [
          #v(6pt)
          #block(
            width: 100%,
            inset: 6pt,
            radius: 3pt,
            fill: rgb(248, 250, 252),
          )[
            #text(size: 9pt, weight: "semibold", fill: accent-color)[Psychological:]
            #text(size: 9pt)[ #psychological]
          ]
        ]

        // Shadow aspect
        #if shadow != none and shadow != "" [
          #v(4pt)
          #block(
            width: 100%,
            inset: 6pt,
            radius: 3pt,
            fill: rgb(254, 249, 243),
            stroke: 0.5pt + rgb(234, 179, 133),
          )[
            #text(size: 9pt, weight: "semibold", fill: rgb(180, 100, 50))[Shadow:]
            #text(size: 9pt)[ #shadow]
          ]
        ]
      ]
    )
  ]
  #v(12pt)
]

// =============================================================================
// Card Relationships
// =============================================================================

#if show_relationships and relationships.len() > 0 [
  #section-heading("Card Relationships")

  #for rel in relationships [
    #let card1 = rel.at(0)
    #let card2 = rel.at(1)
    #let rel_type = rel.at(2)
    #let interp = rel.at(3)

    #block(
      width: 100%,
      inset: 10pt,
      radius: 4pt,
      fill: relationship-bg,
      stroke: 0.5pt + relationship-border,
    )[
      #text(weight: "bold")[#card1]
      #text(fill: gray)[#rel_type]
      #text(weight: "bold")[#card2]
      #v(4pt)
      #text(size: 10pt)[#interp]
    ]
    #v(8pt)
  ]
]

// =============================================================================
// Synthesized Reading (only shown for LLM-generated readings)
// =============================================================================

#if show_synthesis [
  #section-heading("Reading")

  #block(
    width: 100%,
    inset: 16pt,
    radius: 6pt,
    fill: rgb(247, 250, 252),
  )[
    #set par(leading: 0.8em)
    #synthesis
  ]
]

// =============================================================================
// Prompt Appendix (Debug/Examination)
// =============================================================================

#if show_prompt_appendix [
  #pagebreak()

  #align(center)[
    #text(size: 18pt, weight: "bold", fill: accent-color)[Appendix: LLM Prompt]
    #v(0.5em)
    #text(size: 10pt, fill: gray)[For examination and prompt refinement]
  ]
  #v(1em)

  #if system_prompt != none [
    #section-heading("System Prompt")
    #block(
      width: 100%,
      inset: 12pt,
      radius: 4pt,
      fill: rgb(248, 250, 252),
      stroke: 0.5pt + card-border,
    )[
      #set text(font: "Menlo", size: 9pt)
      #set par(leading: 0.6em)
      #system_prompt
    ]
    #v(1em)
  ]

  #if user_prompt != none [
    #section-heading("User Prompt")
    #block(
      width: 100%,
      inset: 12pt,
      radius: 4pt,
      fill: rgb(248, 250, 252),
      stroke: 0.5pt + card-border,
    )[
      #set text(font: "Menlo", size: 9pt)
      #set par(leading: 0.6em)
      #user_prompt
    ]
  ]
]

// =============================================================================
// Footer
// =============================================================================

#v(2em)
#align(center)[
  #line(length: 30%, stroke: 0.5pt + gray)
  #v(0.5em)
  #text(size: 9pt, fill: gray)[Generated by Arcanite]
]
