// Typst CV for Siddhartha Srinivasa
// Matches formatting of LaTeX version

// Page setup
#set page(
  paper: "us-letter",
  margin: 0.75in,
  numbering: none,
)

// Font and text settings
#set text(
  font: "Palatino",
  size: 10pt,
)

#set par(
  justify: false,
  leading: 0.65em,
)

// Hyperlink styling (blue links like LaTeX hyperref)
#show link: set text(fill: rgb("#0000EE"))

// Section styling - bold, large, with horizontal rule
#show heading.where(level: 1): it => {
  set text(size: 12pt, weight: "bold")
  block(above: 10pt, below: 10pt)[
    #it.body
    #v(-8pt)
    #line(length: 100%, stroke: 0.5pt)
  ]
}

// Subsection styling - bold, no rule
#show heading.where(level: 2): it => {
  set text(size: 10pt, weight: "bold")
  block(above: 0pt, below: 10pt)[#it.body]
}

// Title
#align(center)[
  #text(size: 17pt, weight: "bold")[Prof. Siddhartha Srinivasa]
]

#v(10pt)

// Header - Contact Information
#align(center)[
  #table(
    columns: (auto, auto, auto),
    stroke: none,
    align: (left, right, left),
    row-gutter: 4pt,
    [The Personal Robotics Lab], [*Phone:*], [(412) 973 9615],
    [Paul G. Allen School of Computer Science & Engineering], [*Twitter:*], link("https://twitter.com/siddhss5")[\@siddhss5],
    [University of Washington], [*Email:*], link("mailto:siddh@cs.uw.edu")[siddh\@cs.uw.edu],
    [185 E Stevens Way NE], [*WWW:*], link("https://goodrobot.ai")[https://goodrobot.ai],
    [Seattle, WA - 98195], [*Admin:*], [Lisa Merlin (#link("mailto:lmerlin@cs.washington.edu")[lmerlin\@cs.washington.edu])],
  )
]

// Employment Section
= Employment

Professor #h(1fr) 2023-#h(0.5em)\
Boeing Endowed Professor in Computer Science & Engineering #h(1fr) 2017-23\
Computer Science & Engineering Department,
University of Washington\
\
Finmeccanica Associate Professor in Computer Science#h(1fr) 2013-17\
Associate Professor#h(1fr) 2011-13\
The Robotics Institute, Carnegie Mellon University\
\
Member, Board of Directors, Zordi Inc.#h(1fr) 2021-#h(0.5em)\
Distinguished Engineer, Cruise Inc.#h(1fr) 2022-25\
Director, Robotics AI, Amazon Inc.#h(1fr) 2018-22\
First Wave Founder, Berkshire Grey Inc.#h(1fr) 2014-18\
Senior Research Scientist, Intel Labs Pittsburgh #h(1fr) 2005-11

// Education Section
= Education

Ph.D., Carnegie Mellon University (CMU)#h(1fr) August 2005\
Advisors: Michael Erdmann & Matthew Mason#h(1fr) Thesis: _Control Synthesis for Dynamic Contact Manipulation_\
\
B. Tech., Indian Institute of Technology Madras (IITM)#h(1fr) August 1999\
Advisor: A. Radhakrishnan#h(1fr)
Thesis: _Reverse Engineering using the Structured Lighting Technique_

// Honors and Awards (from CSV)
= Honors and Awards

#let awards_data = csv("data/awards.csv")
#let awards_headers = awards_data.first()
#let awards_rows = awards_data.slice(1)
#for row in awards_rows [
  #row.at(0) #h(1fr) #row.at(1)\
]

// Mentoring Section (with conditional current/alumni logic)
= Mentoring

// Load CSV files
#let students_phd_raw = csv("data/students-phd.csv")
#let students_ms_raw = csv("data/students-ms.csv")
#let postdocs_raw = csv("data/postdocs.csv")

// Convert to dictionaries for easier access
#let csv_to_dict(data) = {
  let headers = data.first()
  data.slice(1).map(row => {
    let dict = (:)
    for (i, header) in headers.enumerate() {
      dict.insert(header, row.at(i))
    }
    dict
  })
}

#let students_phd = csv_to_dict(students_phd_raw)
#let students_ms = csv_to_dict(students_ms_raw)
#let postdocs = csv_to_dict(postdocs_raw)

// Helper function to show name with optional coadvisor
#let show_name(name, coadvisor) = {
  if coadvisor != "" {
    name + " (+" + coadvisor + ")"
  } else {
    name
  }
}

// Current PhD Students
#let current_phd = students_phd.filter(s => s.at("Finish") == "")
#if current_phd.len() > 0 [
  == Current Ph.D. Students
  #for student in current_phd [
    #show_name(student.at("Name"), student.at("Coadvisor")) #h(1fr) #student.at("Start")-

  ]
]

// Current MS Students
#let current_ms = students_ms.filter(s => s.at("Finish") == "")
#if current_ms.len() > 0 [
  == Current M.S. Students
  #for student in current_ms [
    #show_name(student.at("Name"), student.at("Coadvisor")) #h(1fr) #student.at("Start")-

  ]
]

// Current Postdoctoral Fellows
#let current_postdocs = postdocs.filter(p => p.at("Finish") == "")
#if current_postdocs.len() > 0 [
  == Current Postdoctoral Fellows
  #for postdoc in current_postdocs [
    #show_name(postdoc.at("Name"), postdoc.at("Coadvisor")) #h(1fr) #postdoc.at("Start")-

  ]
]

// Alumni - Postdoctoral Fellows
#let alumni_postdocs = postdocs.filter(p => p.at("Finish") != "")
#if alumni_postdocs.len() > 0 [
  == Alumni - Postdoctoral Fellows
  #for postdoc in alumni_postdocs [
    #let name_text = show_name(postdoc.at("Name"), postdoc.at("Coadvisor"))
    #name_text #h(1fr) #postdoc.at("Start")-#postdoc.at("Finish")\
    #align(right)[#postdoc.at("NowAt")]\
    \
  ]
]

// Alumni - Ph.D.
#let alumni_phd = students_phd.filter(s => s.at("Finish") != "")
#if alumni_phd.len() > 0 [
  == Alumni - Ph.D.
  #for student in alumni_phd [
    #let name_text = show_name(student.at("Name"), student.at("Coadvisor"))
    #name_text #h(1fr) #student.at("Start")-#student.at("Finish")\
    _#student.at("Title")_#h(1fr) #student.at("NowAt")\
    \
  ]
]

// Alumni - M.S.
#let alumni_ms = students_ms.filter(s => s.at("Finish") != "")
#if alumni_ms.len() > 0 [
  == Alumni - M.S.
  #for student in alumni_ms [
    #let name_text = show_name(student.at("Name"), student.at("Coadvisor"))
    #name_text #h(1fr) #student.at("Start")-#student.at("Finish")\
    _#student.at("Title")_#h(1fr) #student.at("NowAt")\
    \
  ]
]

// Alumni - Other (static from mentoring.tex)
== Alumni - Other

Ajinkya Kamat, Staff #h(1fr) 2018-2019\
Research: _Outdoor Unstructured Mobile Manipulation_ #h(1fr) MRSD @ CMU\
\
Youngsun Kim, Staff #h(1fr) 2017-2019\
Research: _Robot-Assisted Feeding_ #h(1fr) Engineer @ Zordi\
\
Hanjun Song, Staff #h(1fr) 2016-2019\
Research: _Sensing Shear Forces During Food Manipulation_ #h(1fr) Ph.D. @ MIT\
\
Rachel Holladay, B.S. #h(1fr) 2013-2017\
Thesis: _Following Paths in Task Space: Distance Metrics and Planning Algorithms_ #h(1fr) Assistant Professor @ Penn\
\
Pyry Matikainen, Teaching Fellow #h(1fr) 2015-2017\
Research: _Visual Computing_\
\

// Ph.D Thesis Committees (static from mentoring.tex)
== Ph.D Thesis Committees

Vinitha Ranganeni (UW) #h(1fr) 2024\
Nick Walker (UW) #h(1fr) 2024\
Nathan Hatch (UW) #h(1fr) 2024\
Mohak Bharadwaj (UW) #h(1fr) 2024\
Anqi Li (UW) #h(1fr) 2024\
Ekta Samani (UW) #h(1fr) 2023\
Christopher Xie (UW) #h(1fr) 2021\
Senka Krivic (University of Innsbruck) #h(1fr) 2019\
Parker Owan (UW) #h(1fr) 2019\
Arunkumar Byravan (UW) #h(1fr) 2019\
Rahul Warrier (UW) #h(1fr) 2018\
Justin Huang (UW) #h(1fr) 2018\
Connor Schenk (UW) #h(1fr) 2017-18\
Kiril Solovey (Technion) #h(1fr) 2018\
Sanjiban Choudhury (CMU) #h(1fr) 2013-17\
Venkatraman Narayanan (CMU)#h(1fr) 2013-17\
Breelyn Kane Styler (CMU) #h(1fr) 2011-18\
Mike Phillips (CMU) #h(1fr) 2011-15\
Alberto Rodriguez (CMU) #h(1fr) 2007-13\
Ross Knepper (CMU) #h(1fr) 2006-11\
Nathan Ratliff (CMU) #h(1fr) 2004-09\

// Selected Press Coverage
= Selected Press Coverage (#link("https://personalrobotics.cs.washington.edu/press/")[Longer list])

#let press_raw = csv("data/press.csv")
#let press = csv_to_dict(press_raw)
#for item in press [
  #link(item.at("Link"))[#item.at("Title")] #h(1fr) #item.at("Source"), #item.at("Year")\
]

// Grants Section
= Grants (excludes unrestricted gifts)

#let grants_raw = csv("data/grants.csv")
#let grants = csv_to_dict(grants_raw)
#for grant in grants [
  #grant.at("Funder") #h(1fr) #grant.at("Start")-#grant.at("Finish")\
  _#grant.at("Title")_ #h(1fr) #if grant.at("PI") == "" [PI] else [co-PI, PI: #grant.at("PI")]\
  #grant.at("Program")\
  \
]

// Publications Section
= Publications (#link("https://scholar.google.com/citations?user=RCi98EAAAAAJ&hl=en")[Google Scholar])

_Publications section placeholder - to be implemented with BibTeX bibliography and author filtering._
