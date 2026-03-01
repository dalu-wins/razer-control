#!/bin/bash
set -e # Stoppt bei Fehlern

echo "--- 1. Installiere Python-Paket (Editable Mode) ---"
# -v zeigt den Fortschritt, damit du siehst, wo er hängt
pip install .

echo "--- 2. Kopiere Desktop-Datei ---"
mkdir -p ~/.local/share/applications
cp de.dalu_wins.RazerControl.desktop ~/.local/share/applications/

echo "--- 3. Aktualisiere Datenbanken ---"
update-desktop-database ~/.local/share/applications
gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor

echo "Fertig! Falls es nicht im Menü erscheint, logge dich einmal neu ein."