#!/bin/bash

echo "--- 1. Entferne Python-Paket via Pip ---"
# Deinstalliert das Paket, egal ob normal oder im 'editable' Modus installiert
pip uninstall -y razer-control

echo "--- 2. Entferne manuellen Entrypoint & Desktop-Datei ---"
rm -f ~/.local/bin/razer-control
rm -f ~/.local/share/applications/de.dalu_wins.RazerControl.desktop

echo "--- 3. Aktualisiere System-Datenbanken ---"
update-desktop-database ~/.local/share/applications
gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor 2>/dev/null || true

echo "-----------------------------------------------"
echo "Deinstallation abgeschlossen!"
echo "Die App wurde vollständig aus dem System entfernt."