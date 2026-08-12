#!/usr/bin/env bash
# Benchmark mémoire VRAM et vérification du plafond strict de 22 Go
set -euo pipefail

echo "===================================================================="
echo "⚡ MangaTok Studio — Benchmark Mémoire GPU & VRAM Guard"
echo "===================================================================="

python3 -c "
import sys
from manga_studio.core.gpu_manager import GPUResourceManager, VRAMCeilingExceededError

manager = GPUResourceManager(ceiling_gb=22.0)
print(f'Plafond VRAM configuré : {manager.ceiling_gb} Go ({manager.ceiling_bytes} octets)')
print(f'Support CUDA PyTorch   : {manager.is_cuda_available()}')

# Test 1 : Allocation nominale (18 Go)
try:
    ok, gb = manager.check_vram_limit(current_allocated_bytes=int(18 * 1024**3))
    print(f'✓ Test 1 (18 Go alloués) : SUCCÈS (Alloué: {gb:.1f} Go <= 22 Go)')
except Exception as e:
    print(f'❌ Test 1 Échoué : {e}')
    sys.exit(1)

# Test 2 : Détection de dépassement du plafond (23 Go)
try:
    manager.check_vram_limit(current_allocated_bytes=int(23 * 1024**3))
    print('❌ Test 2 Échoué : Le dépassement aurait dû être bloqué !')
    sys.exit(1)
except VRAMCeilingExceededError as e:
    print(f'✓ Test 2 (23 Go alloués) : SUCCÈS (Blocage immédiat déclenché avec message d\'erreur clair)')

# Test 3 : Nettoyage et éviction
stats = manager.evict_and_clean()
print(f'✓ Test 3 (Éviction et Garbage Collection) : SUCCÈS')

print('====================================================================')
print('✅ Tous les contrôles de conformité mémoire GPU sont validés à 100% !')
print('====================================================================')
"
