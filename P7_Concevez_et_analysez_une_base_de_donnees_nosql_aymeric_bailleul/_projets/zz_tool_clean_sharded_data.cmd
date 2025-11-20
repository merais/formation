@echo off
echo ====================================================================================================
echo NETTOYAGE DES DONNEES DU CLUSTER SHARDE
echo ====================================================================================================
echo.
echo Ce script va supprimer toutes les donnees dans data_replicatset_sharded/
echo tout en conservant l'arborescence des dossiers.
echo.
pause

cd /d "%~dp0"

echo.
echo Suppression des donnees du Config Server 1...
del /Q /F "data_replicatset_sharded\config1\*.*" 2>nul
for /d %%p in ("data_replicatset_sharded\config1\*") do rmdir "%%p" /s /q 2>nul

echo Suppression des donnees du Config Server 2...
del /Q /F "data_replicatset_sharded\config2\*.*" 2>nul
for /d %%p in ("data_replicatset_sharded\config2\*") do rmdir "%%p" /s /q 2>nul

echo.
echo Suppression des donnees du Shard 1 - data_paris...
del /Q /F "data_replicatset_sharded\shard1\data_paris\*.*" 2>nul
for /d %%p in ("data_replicatset_sharded\shard1\data_paris\*") do rmdir "%%p" /s /q 2>nul

echo Suppression des donnees du Shard 1 - data_lyon...
del /Q /F "data_replicatset_sharded\shard1\data_lyon\*.*" 2>nul
for /d %%p in ("data_replicatset_sharded\shard1\data_lyon\*") do rmdir "%%p" /s /q 2>nul

echo Suppression des donnees du Shard 1 - arbiter...
del /Q /F "data_replicatset_sharded\shard1\arbiter\*.*" 2>nul
for /d %%p in ("data_replicatset_sharded\shard1\arbiter\*") do rmdir "%%p" /s /q 2>nul

echo.
echo Suppression des donnees du Shard 2 - data_paris...
del /Q /F "data_replicatset_sharded\shard2\data_paris\*.*" 2>nul
for /d %%p in ("data_replicatset_sharded\shard2\data_paris\*") do rmdir "%%p" /s /q 2>nul

echo Suppression des donnees du Shard 2 - data_lyon...
del /Q /F "data_replicatset_sharded\shard2\data_lyon\*.*" 2>nul
for /d %%p in ("data_replicatset_sharded\shard2\data_lyon\*") do rmdir "%%p" /s /q 2>nul

echo Suppression des donnees du Shard 2 - arbiter...
del /Q /F "data_replicatset_sharded\shard2\arbiter\*.*" 2>nul
for /d %%p in ("data_replicatset_sharded\shard2\arbiter\*") do rmdir "%%p" /s /q 2>nul

echo.
echo Suppression des fichiers logs...
del /Q /F "data_replicatset_sharded\_logs\*.*" 2>nul

echo.
echo ====================================================================================================
echo NETTOYAGE TERMINE
echo ====================================================================================================
echo.
echo L'arborescence des dossiers a ete conservee.
echo Vous pouvez maintenant redemarrer votre cluster MongoDB.
echo.
pause
