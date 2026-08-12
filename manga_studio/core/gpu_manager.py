"""Gestionnaire de mémoire GPU et surveillance du plafond de VRAM (RTX 4090 - 22 Go)."""

import gc
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class VRAMCeilingExceededError(Exception):
    """Exception levée lorsque la mémoire VRAM mesurée dépasse le plafond alloué."""
    pass


class GPUResourceManager:
    """Surveillance et régulation de la VRAM GPU."""

    def __init__(self, ceiling_gb: float = 22.0, device_id: int = 0):
        self.ceiling_gb = ceiling_gb
        self.device_id = device_id
        self.ceiling_bytes = int(ceiling_gb * (1024 ** 3))

    def is_cuda_available(self) -> bool:
        """Vérifie si CUDA et PyTorch sont disponibles sur l'hôte."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    def evict_and_clean(self) -> Dict[str, float]:
        """Libère explicitement la mémoire GPU et force le ramasse-miettes."""
        stats = {"allocated_gb": 0.0, "reserved_gb": 0.0}
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
                alloc = torch.cuda.memory_allocated(self.device_id)
                res = torch.cuda.memory_reserved(self.device_id)
                stats["allocated_gb"] = alloc / (1024 ** 3)
                stats["reserved_gb"] = res / (1024 ** 3)
                logger.info(f"[GPU] Cache vidé. Mémoire allouée: {stats['allocated_gb']:.2f} Go, Réservée: {stats['reserved_gb']:.2f} Go")
        except Exception as e:
            logger.debug(f"[GPU] Nettoyage GPU ignoré ou non supporté: {e}")
        return stats

    def check_vram_limit(self, current_allocated_bytes: Optional[int] = None) -> Tuple[bool, float]:
        """Vérifie si la VRAM respecte le plafond de 22 Go."""
        allocated = current_allocated_bytes
        if allocated is None:
            try:
                import torch
                if torch.cuda.is_available():
                    allocated = torch.cuda.memory_allocated(self.device_id)
                else:
                    allocated = 0
            except Exception:
                allocated = 0

        allocated_gb = allocated / (1024 ** 3)
        if allocated > self.ceiling_bytes:
            msg = f"Dépassement du plafond VRAM ! Alloué: {allocated_gb:.2f} Go > Plafond: {self.ceiling_gb:.2f} Go"
            logger.error(msg)
            self.evict_and_clean()
            raise VRAMCeilingExceededError(msg)

        return True, allocated_gb
