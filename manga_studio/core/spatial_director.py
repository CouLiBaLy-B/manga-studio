"""Directeur spatial et composition multi-personnages pour la cohérence de scène."""

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from manga_studio.core.models.character import CharacterBible


class CharacterSpatialPlacement(BaseModel):
    """Positionnement d'un personnage dans l'espace de la caméra."""
    character_id: str
    horizontal_position: Literal["left", "center", "right", "foreground", "background"]
    facing_direction: Literal["facing_camera", "facing_left", "facing_right", "three_quarters_view"]
    depth_layer: Literal["foreground", "midground", "background"] = "midground"
    pose_description: str = ""


class SceneSpatialDirector:
    """Calcule la mise en scène et la disposition géométrique des personnages."""

    @classmethod
    def arrange_scene(
        cls,
        character_ids: List[str],
        character_bible: CharacterBible,
        emotion: str = "épique"
    ) -> List[CharacterSpatialPlacement]:
        """Détermine un placement équilibré pour 1 à 9 personnages."""
        placements: List[CharacterSpatialPlacement] = []
        n_chars = len(character_ids)

        if n_chars == 1:
            cid = character_ids[0]
            placements.append(
                CharacterSpatialPlacement(
                    character_id=cid,
                    horizontal_position="center",
                    facing_direction="three_quarters_view",
                    depth_layer="foreground",
                    pose_description="Majestic central stance, dominant framing."
                )
            )
        elif n_chars == 2:
            # Face à face ou dialogue
            placements.append(
                CharacterSpatialPlacement(
                    character_id=character_ids[0],
                    horizontal_position="left",
                    facing_direction="facing_right",
                    depth_layer="midground",
                    pose_description="Standing on the left side, addressing the companion."
                )
            )
            placements.append(
                CharacterSpatialPlacement(
                    character_id=character_ids[1],
                    horizontal_position="right",
                    facing_direction="facing_left",
                    depth_layer="midground",
                    pose_description="Standing on the right side, engaging in dialogue."
                )
            )
        else:
            # 3 personnages ou plus
            positions = ["left", "center", "right", "foreground", "background"]
            for idx, cid in enumerate(character_ids):
                pos = positions[idx % len(positions)]
                depth = "foreground" if idx == 0 else ("midground" if idx == 1 else "background")
                placements.append(
                    CharacterSpatialPlacement(
                        character_id=cid,
                        horizontal_position=pos,
                        facing_direction="facing_camera" if pos == "center" else ("facing_right" if pos == "left" else "facing_left"),
                        depth_layer=depth,
                        pose_description=f"Positioned on the {pos} depth {depth}."
                    )
                )

        return placements

    @classmethod
    def compile_spatial_prompt_clause(cls, placements: List[CharacterSpatialPlacement]) -> str:
        """Génère la clause spatiale en anglais pour guider le modèle de diffusion."""
        clauses = []
        for p in placements:
            clauses.append(
                f"[Spatial Arrangement: {p.character_id} positioned on the {p.horizontal_position} ({p.depth_layer}), {p.facing_direction}. {p.pose_description}]"
            )
        return " ".join(clauses)
