"""Tests unitaires pour le gestionnaire GPU et la surveillance du plafond VRAM (22 Go)."""

import pytest
from manga_studio.core.gpu_manager import GPUResourceManager, VRAMCeilingExceededError


def test_gpu_manager_normal_allocation():
    """Vérifie qu'une allocation sous le plafond de 22 Go est acceptée."""
    manager = GPUResourceManager(ceiling_gb=22.0)
    
    # 18 Go alloués (< 22 Go)
    allocated_18gb = 18 * (1024 ** 3)
    ok, gb = manager.check_vram_limit(current_allocated_bytes=allocated_18gb)
    assert ok is True
    assert round(gb, 1) == 18.0


def test_gpu_manager_ceiling_exceeded_raises_error():
    """Vérifie qu'un dépassement du plafond de 22 Go lève VRAMCeilingExceededError."""
    manager = GPUResourceManager(ceiling_gb=22.0)
    
    # 23 Go alloués (> 22 Go)
    allocated_23gb = 23 * (1024 ** 3)
    with pytest.raises(VRAMCeilingExceededError) as exc_info:
        manager.check_vram_limit(current_allocated_bytes=allocated_23gb)
    assert "Dépassement du plafond VRAM" in str(exc_info.value)


def test_gpu_manager_eviction_cleanup():
    """Vérifie l'exécution du nettoyage sans erreur même en l'absence de CUDA physique."""
    manager = GPUResourceManager(ceiling_gb=22.0)
    stats = manager.evict_and_clean()
    assert isinstance(stats, dict)
    assert "allocated_gb" in stats
