;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "1-introduccion"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("article" "11pt" "a4paper")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("inputenc" "utf8") ("fontenc" "T1") ("babel" "spanish" "es-nodecimaldot") ("lmodern" "") ("amsmath" "") ("amssymb" "") ("mathtools" "") ("graphicx" "") ("xcolor" "") ("geometry" "") ("enumitem" "") ("microtype" "")))
   (TeX-run-style-hooks
    "latex2e"
    "article"
    "art11"
    "inputenc"
    "fontenc"
    "babel"
    "lmodern"
    "amsmath"
    "amssymb"
    "mathtools"
    "graphicx"
    "xcolor"
    "geometry"
    "enumitem"
    "microtype")
   (TeX-add-symbols
    '("braket" 2)
    '("bra" 1)
    '("ket" 1)
    '("concept" 1)
    "hc"
    "Tr"
    "Diffs"))
 :latex)

