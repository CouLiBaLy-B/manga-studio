'use client';

import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Sparkles, 
  Film, 
  UserCheck, 
  ShieldCheck, 
  Sliders, 
  UploadCloud, 
  FileText, 
  Layers, 
  CheckCircle2, 
  AlertTriangle, 
  Share2, 
  Download, 
  RefreshCw, 
  Eye, 
  Edit3, 
  Save, 
  ArrowUp, 
  ArrowDown 
} from 'lucide-react';

export default function MangaTokDashboard() {
  const [activeTab, setActiveTab] = useState<'studio' | 'bible' | 'storyboard' | 'qc' | 'player' | 'manifest'>('studio');
  
  // États d'importation
  const [storyId, setStoryId] = useState('mythe_ra');
  const [taleText, setTaleText] = useState(`Au commencement des temps, Râ, le grand dieu solaire, régnait sur l'Égypte avec splendeur et bienveillance. Chaque soir, il montait à bord de sa barque céleste sacrée pour traverser le ciel étoilé.

Tandis que la nuit tombait sur le Nil, les fidèles gardiens du temple s'inclinèrent avec un profond respect. « La route du ciel est prête, Seigneur Râ », déclara le premier gardien d'une voix solennelle. Râ sourit et répondit : « Que la lumière ne s'éteigne jamais dans vos cœurs ».

La barque d'or quitta doucement la rive sacrée pour s'élever au milieu des constellations. Le dieu veillait sur le monde des mortels, garantissant que chaque aube apporterait un jour nouveau.`);
  
  const [stylePreset, setStylePreset] = useState('watercolor_mythology');
  const [deploymentProfile, setDeploymentProfile] = useState('research');
  const [territory, setTerritory] = useState('EU');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);
  
  // États d'exécution et données
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationStep, setGenerationStep] = useState(0);
  const [bibleData, setBibleData] = useState<any>(null);
  const [storyboardData, setStoryboardData] = useState<any>(null);
  const [qcData, setQcData] = useState<any[]>([]);
  const [manifestEvents, setManifestEvents] = useState<any[]>([]);
  const [socialData, setSocialData] = useState<any>(null);
  const [editingSceneId, setEditingSceneId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<any>({});

  const stylePresets = [
    { key: 'watercolor_mythology', name: 'Mythologie & Or Sacré', desc: 'Enluminures divines, sumi-e et dorures royales.' },
    { key: 'shonen_epic', name: 'Shōnen Épique', desc: 'Traits dynamiques, contrastes forts et action explosive.' },
    { key: 'seinen_dark_fantasy', name: 'Seinen Dark Fantasy', desc: 'Clair-obscur dramatique, textures brutes et ombres profondes.' },
    { key: 'ghibli_poetic', name: 'Ghibli Poétique', desc: 'Aquarelle douce, nature luxuriante et lumière pastel.' },
    { key: 'cyberpunk_neo_tokyo', name: 'Cyberpunk Néo-Tokyo', desc: 'Néons futuristes, pluie nocturne et reflets holographiques.' }
  ];

  // Chargement initial des données
  useEffect(() => {
    fetchRunData('conte');
  }, []);

  const fetchRunData = async (targetId: string) => {
    try {
      const bRes = await fetch(`/api/runs/${targetId}/bible`);
      if (bRes.ok) setBibleData(await bRes.json());

      const sRes = await fetch(`/api/runs/${targetId}/storyboard`);
      if (sRes.ok) setStoryboardData(await sRes.json());

      const qRes = await fetch(`/api/runs/${targetId}/qc`);
      if (qRes.ok) setQcData(await qRes.json());

      const mRes = await fetch(`/api/runs/${targetId}/manifest`);
      if (mRes.ok) setManifestEvents(await mRes.json());

      const socRes = await fetch(`/api/runs/${targetId}/social`);
      if (socRes.ok) setSocialData(await socRes.json());
    } catch (e) {
      console.warn('Données initiales non encore générées:', e);
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files).slice(0, 9);
      setSelectedFiles(files);
      const previews = files.map(file => URL.createObjectURL(file));
      setImagePreviews(previews);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setGenerationStep(1);

    const formData = new FormData();
    formData.append('story_id', storyId);
    formData.append('tale_text', taleText);
    formData.append('profile', deploymentProfile);
    formData.append('territory', territory);
    formData.append('style_preset', stylePreset);

    selectedFiles.forEach((file) => {
      formData.append('character_files', file);
    });

    try {
      // Simulation des étapes pour feedback visuel
      const interval = setInterval(() => {
        setGenerationStep(prev => (prev < 6 ? prev + 1 : prev));
      }, 500);

      const res = await fetch('/api/upload-and-run', {
        method: 'POST',
        body: formData,
      });

      clearInterval(interval);
      setGenerationStep(7);

      if (res.ok) {
        await fetchRunData(storyId);
        setActiveTab('player');
      } else {
        alert('Erreur lors de la génération.');
      }
    } catch (err) {
      console.error(err);
      alert('Erreur réseau.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleEditScene = (seg: any) => {
    setEditingSceneId(seg.scene_id);
    setEditForm({
      titre: seg.titre,
      frame: seg.frame,
      prompt_ia: seg.prompt_ia,
      duree_s: seg.duree_s,
      emotion: seg.emotion,
      plan: seg.plan,
    });
  };

  const handleSaveScene = async (sceneId: string) => {
    try {
      const res = await fetch(`/api/runs/${storyId}/segments/${sceneId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editForm),
      });
      if (res.ok) {
        setEditingSceneId(null);
        await fetchRunData(storyId);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleReorder = async (idx: number, direction: 'up' | 'down') => {
    if (!storyboardData || !storyboardData.segments) return;
    const segments = [...storyboardData.segments];
    const targetIdx = direction === 'up' ? idx - 1 : idx + 1;
    if (targetIdx < 0 || targetIdx >= segments.length) return;

    const temp = segments[idx];
    segments[idx] = segments[targetIdx];
    segments[targetIdx] = temp;

    const sceneIds = segments.map(s => s.scene_id);
    try {
      await fetch(`/api/runs/${storyId}/reorder`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scene_ids_in_order: sceneIds }),
      });
      await fetchRunData(storyId);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-[#090A0F] text-[#F3F4F6] p-6 max-w-7xl mx-auto">
      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-6 border-b border-[#1E2235] mb-8">
        <div>
          <div className="flex items-center gap-3">
            <span className="text-3xl">⚡</span>
            <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-[#F4C542] via-yellow-200 to-amber-400 bg-clip-text text-transparent">
              MangaTok Studio
            </h1>
            <span className="text-xs uppercase px-2.5 py-0.5 rounded-full bg-[#F4C542]/10 text-[#F4C542] border border-[#F4C542]/30 font-mono font-semibold">
              Mode « Conte animé »
            </span>
          </div>
          <p className="text-sm text-[#9CA3AF] mt-1">
            Orchestrateur Hexagonal LangGraph — TikTok & Reels 9:16 Video Synthesis
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-xs font-mono px-3 py-1.5 rounded-lg bg-[#12141F] border border-[#1E2235] text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            RTX 4090 VRAM GUARD: 22.0 GB
          </span>
          <button 
            onClick={() => fetchRunData(storyId)}
            className="p-2 rounded-lg bg-[#12141F] hover:bg-[#1E2235] border border-[#1E2235] text-[#9CA3AF] hover:text-white transition"
            title="Rafraîchir les données"
          >
            <RefreshCw size={16} />
          </button>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="flex flex-wrap gap-2 mb-8 bg-[#12141F]/80 p-1.5 rounded-xl border border-[#1E2235]">
        {[
          { id: 'studio', label: '1. Studio & Import', icon: Sliders },
          { id: 'bible', label: '2. Fiches Personnages', icon: UserCheck },
          { id: 'storyboard', label: '3. Storyboard Studio', icon: Film },
          { id: 'qc', label: '4. Contrôle Qualité', icon: ShieldCheck },
          { id: 'player', label: '5. Lecteur 9:16 & Formats', icon: Play },
          { id: 'manifest', label: '6. Audit & Manifest', icon: Layers },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm transition-all ${
                isActive
                  ? 'bg-[#F4C542] text-black shadow-lg shadow-[#F4C542]/20 font-semibold'
                  : 'text-[#9CA3AF] hover:text-white hover:bg-[#1E2235]'
              }`}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </nav>

      {/* CONTENU DES ONGLETS */}

      {/* 1. STUDIO & IMPORT */}
      {activeTab === 'studio' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {/* Texte du Conte */}
            <div className="bg-[#12141F] border border-[#1E2235] rounded-xl p-5">
              <div className="flex justify-between items-center mb-3">
                <h2 className="text-base font-semibold text-[#F4C542] flex items-center gap-2">
                  <FileText size={18} />
                  Texte du Conte (Français)
                </h2>
                <span className="text-xs text-[#9CA3AF] font-mono">{taleText.length} caractères</span>
              </div>
              <textarea
                value={taleText}
                onChange={(e) => setTaleText(e.target.value)}
                rows={8}
                className="w-full bg-[#0D0E15] border border-[#1E2235] rounded-lg p-3.5 text-sm text-[#F3F4F6] focus:outline-none focus:border-[#F4C542] font-sans leading-relaxed"
                placeholder="Écrivez ou collez votre conte en français..."
              />
            </div>

            {/* Importation des Images Personnages (1 à 9) */}
            <div className="bg-[#12141F] border border-[#1E2235] rounded-xl p-5">
              <h2 className="text-base font-semibold text-[#F4C542] flex items-center gap-2 mb-3">
                <UploadCloud size={18} />
                Images Canoniques des Personnages (1 à 9)
              </h2>
              
              <label className="border-2 border-dashed border-[#1E2235] hover:border-[#F4C542]/60 rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer bg-[#0D0E15]/50 transition group">
                <UploadCloud size={32} className="text-[#9CA3AF] group-hover:text-[#F4C542] transition mb-2" />
                <span className="text-sm font-medium">Glissez vos images ou cliquez pour importer</span>
                <span className="text-xs text-[#9CA3AF] mt-1">PNG, JPG, WEBP — Maximum 9 fichiers</span>
                <input 
                  type="file" 
                  multiple 
                  accept="image/*" 
                  onChange={handleImageUpload} 
                  className="hidden" 
                />
              </label>

              {imagePreviews.length > 0 && (
                <div className="grid grid-cols-3 sm:grid-cols-5 gap-3 mt-4">
                  {imagePreviews.map((src, i) => (
                    <div key={i} className="relative group rounded-lg overflow-hidden border border-[#1E2235] aspect-square bg-black">
                      <img src={src} alt={`Preview ${i}`} className="w-full h-full object-cover" />
                      <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 flex items-center justify-center text-[10px] text-white p-1 text-center transition">
                        {selectedFiles[i]?.name}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Paramètres & Bouton d'action */}
          <div className="space-y-6">
            <div className="bg-[#12141F] border border-[#1E2235] rounded-xl p-5 space-y-4">
              <h2 className="text-base font-semibold text-[#F4C542] flex items-center gap-2">
                <Sliders size={18} />
                Paramètres de Rendu
              </h2>

              <div>
                <label className="text-xs text-[#9CA3AF] font-medium block mb-1.5">Identifiant du conte</label>
                <input
                  type="text"
                  value={storyId}
                  onChange={(e) => setStoryId(e.target.value)}
                  className="w-full bg-[#0D0E15] border border-[#1E2235] rounded-lg p-2 text-sm text-white focus:outline-none focus:border-[#F4C542]"
                />
              </div>

              <div>
                <label className="text-xs text-[#9CA3AF] font-medium block mb-1.5">Preset Stylistique Manga</label>
                <select
                  value={stylePreset}
                  onChange={(e) => setStylePreset(e.target.value)}
                  className="w-full bg-[#0D0E15] border border-[#1E2235] rounded-lg p-2 text-sm text-white focus:outline-none focus:border-[#F4C542]"
                >
                  {stylePresets.map(p => (
                    <option key={p.key} value={p.key}>{p.name}</option>
                  ))}
                </select>
                <p className="text-[11px] text-[#9CA3AF] mt-1 italic">
                  {stylePresets.find(p => p.key === stylePreset)?.desc}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-[#9CA3AF] font-medium block mb-1.5">Profil</label>
                  <select
                    value={deploymentProfile}
                    onChange={(e) => setDeploymentProfile(e.target.value)}
                    className="w-full bg-[#0D0E15] border border-[#1E2235] rounded-lg p-2 text-sm text-white focus:outline-none focus:border-[#F4C542]"
                  >
                    <option value="research">Research (Éducatif)</option>
                    <option value="commercial">Commercial (Strict)</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-[#9CA3AF] font-medium block mb-1.5">Territoire</label>
                  <select
                    value={territory}
                    onChange={(e) => setTerritory(e.target.value)}
                    className="w-full bg-[#0D0E15] border border-[#1E2235] rounded-lg p-2 text-sm text-white focus:outline-none focus:border-[#F4C542]"
                  >
                    <option value="EU">Union Européenne (EU)</option>
                    <option value="US">États-Unis (US)</option>
                    <option value="JP">Japon (JP)</option>
                  </select>
                </div>
              </div>

              <button
                onClick={handleGenerate}
                disabled={isGenerating}
                className="w-full mt-4 bg-gradient-to-r from-[#F4C542] to-amber-500 hover:from-yellow-400 hover:to-amber-400 text-black font-bold py-3 px-4 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-[#F4C542]/20 transition disabled:opacity-50"
              >
                {isGenerating ? (
                  <>
                    <RefreshCw size={18} className="animate-spin" />
                    Génération en cours (Étape {generationStep}/7)...
                  </>
                ) : (
                  <>
                    <Sparkles size={18} />
                    Générer la Vidéo Verticale
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 2. FICHES PERSONNAGES */}
      {activeTab === 'bible' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-bold text-[#F4C542] flex items-center gap-2">
              <UserCheck size={20} />
              Bible des Personnages Canoniques (Verrouillée)
            </h2>
            <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-full font-mono">
              LOCKED: TRUE (IMMUABLE)
            </span>
          </div>

          {bibleData ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {bibleData.characters?.map((char: any) => (
                <div key={char.character_id} className="bg-[#12141F] border border-[#1E2235] rounded-xl p-5 space-y-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-lg font-bold text-white">{char.nom}</h3>
                      <p className="text-xs text-[#9CA3AF]">{char.role}</p>
                    </div>
                    <span className="text-[10px] font-mono bg-[#1E2235] px-2 py-0.5 rounded text-amber-300">
                      ID: {char.character_id}
                    </span>
                  </div>

                  {/* Palette de couleurs */}
                  <div>
                    <span className="text-xs text-[#9CA3AF] block mb-1">Palette de couleurs :</span>
                    <div className="flex gap-2">
                      {char.description_physique?.couleurs_hex?.map((hex: string, i: number) => (
                        <div key={i} className="flex items-center gap-1 text-[10px] font-mono bg-[#0D0E15] px-2 py-0.5 rounded border border-[#1E2235]">
                          <span className="w-3 h-3 rounded-full" style={{ backgroundColor: hex }} />
                          {hex}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Attributs physiques */}
                  <div className="bg-[#0D0E15] p-3 rounded-lg text-xs space-y-1 text-[#CBD5E1]">
                    <p><strong>Silhouette :</strong> {char.description_physique?.silhouette}</p>
                    <p><strong>Visage :</strong> {char.description_physique?.visage}</p>
                    <p><strong>Tenue :</strong> {char.description_physique?.tenue}</p>
                    <p><strong>Accessoires :</strong> {char.description_physique?.accessoires_signature?.join(', ')}</p>
                  </div>

                  <div className="flex justify-between items-center text-xs text-[#9CA3AF] pt-2 border-t border-[#1E2235]">
                    <span>🎙️ Voix : {char.voix_suggeree?.ton}</span>
                    <span>🎭 {char.traits_caractere?.join(', ')}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[#9CA3AF] text-sm">Aucune bible chargée. Lancez une génération depuis l'onglet Studio.</p>
          )}
        </div>
      )}

      {/* 3. STORYBOARD STUDIO */}
      {activeTab === 'storyboard' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-bold text-[#F4C542] flex items-center gap-2">
              <Film size={20} />
              Storyboard Structuré & Continuité (Human-in-the-Loop)
            </h2>
            <span className="text-xs text-[#9CA3AF] font-mono">
              Total : {storyboardData?.segments?.length || 0} scènes ({storyboardData?.segments?.reduce((acc: number, s: any) => acc + s.duree_s, 0) || 0}s)
            </span>
          </div>

          <div className="space-y-4">
            {storyboardData?.segments?.map((seg: any, idx: number) => {
              const isEditing = editingSceneId === seg.scene_id;
              return (
                <div key={seg.scene_id} className="bg-[#12141F] border border-[#1E2235] rounded-xl p-5 space-y-3">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold bg-[#F4C542] text-black px-2 py-0.5 rounded">
                        #{seg.ordre}
                      </span>
                      <h3 className="text-base font-bold text-white">{seg.titre}</h3>
                    </div>
                    <div className="flex items-center gap-2">
                      <button onClick={() => handleReorder(idx, 'up')} disabled={idx === 0} className="p-1 rounded hover:bg-[#1E2235] text-[#9CA3AF] disabled:opacity-30">
                        <ArrowUp size={14} />
                      </button>
                      <button onClick={() => handleReorder(idx, 'down')} disabled={idx === (storyboardData.segments.length - 1)} className="p-1 rounded hover:bg-[#1E2235] text-[#9CA3AF] disabled:opacity-30">
                        <ArrowDown size={14} />
                      </button>
                      <button 
                        onClick={() => isEditing ? handleSaveScene(seg.scene_id) : handleEditScene(seg)}
                        className={`text-xs px-3 py-1 rounded-lg font-semibold flex items-center gap-1 ${
                          isEditing ? 'bg-emerald-500 text-black' : 'bg-[#1E2235] text-white hover:bg-[#272C45]'
                        }`}
                      >
                        {isEditing ? <><Save size={12} /> Sauvegarder</> : <><Edit3 size={12} /> Modifier</>}
                      </button>
                    </div>
                  </div>

                  {isEditing ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                      <div>
                        <label className="text-[11px] text-[#F4C542]">Action descriptive (FR) :</label>
                        <textarea
                          value={editForm.frame}
                          onChange={(e) => setEditForm({ ...editForm, frame: e.target.value })}
                          rows={2}
                          className="w-full bg-[#0D0E15] border border-[#272C45] rounded p-2 text-xs text-white"
                        />
                      </div>
                      <div>
                        <label className="text-[11px] text-[#F4C542]">Prompt IA (EN) :</label>
                        <textarea
                          value={editForm.prompt_ia}
                          onChange={(e) => setEditForm({ ...editForm, prompt_ia: e.target.value })}
                          rows={2}
                          className="w-full bg-[#0D0E15] border border-[#272C45] rounded p-2 text-xs text-white"
                        />
                      </div>
                    </div>
                  ) : (
                    <>
                      <p className="text-xs text-[#CBD5E1]"><strong>Action :</strong> {seg.frame}</p>
                      <p className="text-xs text-[#94A3B8] font-mono"><strong>Prompt IA :</strong> {seg.prompt_ia}</p>
                      <div className="flex flex-wrap gap-2 pt-1 text-[11px]">
                        <span className="bg-[#0D0E15] px-2 py-0.5 rounded text-amber-300">⏱️ {seg.duree_s}s</span>
                        <span className="bg-[#0D0E15] px-2 py-0.5 rounded text-blue-300">🎭 {seg.emotion}</span>
                        <span className="bg-[#0D0E15] px-2 py-0.5 rounded text-purple-300">📐 {seg.plan}</span>
                        <span className="bg-[#0D0E15] px-2 py-0.5 rounded text-emerald-300">✨ {seg.transition?.type} ({seg.transition?.duration_s}s)</span>
                      </div>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 4. CONTRÔLE QUALITÉ (QC) */}
      {activeTab === 'qc' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-bold text-[#F4C542] flex items-center gap-2">
              <ShieldCheck size={20} />
              Rapports de Contrôle Qualité (DINOv2 & WER)
            </h2>
            <span className="text-xs text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20 font-mono">
              SEUIL DINOv2: 0.75 | WER MAX: 0.15
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {qcData.map((qc: any, i: number) => (
              <div key={i} className="bg-[#12141F] border border-[#1E2235] rounded-xl p-5 space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-bold text-white">Scène #{i + 1} ({qc.segment_id})</span>
                  <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase ${
                    qc.status === 'passed' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                  }`}>
                    {qc.status}
                  </span>
                </div>

                {/* Score DINOv2 */}
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-[#9CA3AF]">Similarité DINOv2 :</span>
                    <span className="font-mono font-bold text-white">{qc.visual_similarity?.score?.toFixed(2)} / 1.00</span>
                  </div>
                  <div className="w-full bg-[#0D0E15] h-2 rounded-full overflow-hidden">
                    <div 
                      className="bg-emerald-500 h-full rounded-full transition-all" 
                      style={{ width: `${(qc.visual_similarity?.score || 0) * 100}%` }}
                    />
                  </div>
                </div>

                {/* Word Error Rate */}
                <div className="text-xs flex justify-between bg-[#0D0E15] p-2.5 rounded-lg">
                  <span className="text-[#9CA3AF]">WER Audio Français :</span>
                  <span className="font-mono text-emerald-400 font-bold">{((qc.dialogue_wer || 0) * 100).toFixed(1)}%</span>
                </div>

                <div className="text-[11px] text-[#9CA3AF] space-y-1">
                  <p>✓ Audio présent : {qc.audio_present ? 'OUI' : 'NON'}</p>
                  <p>✓ Durée conforme : {qc.duration_ok ? 'OUI' : 'NON'}</p>
                  <p>✓ Recommandation : <strong className="text-white">{qc.recommendation}</strong></p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 5. LECTEUR VIDÉO 9:16 & MULTI-FORMATS */}
      {activeTab === 'player' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Lecteur Vertical */}
          <div className="flex flex-col items-center">
            <div className="w-[280px] h-[500px] bg-black rounded-3xl border-4 border-[#1E2235] overflow-hidden shadow-2xl relative flex items-center justify-center">
              <video 
                src={`/api/media/${storyId}/video`} 
                controls 
                className="w-full h-full object-cover"
                poster="/api/media/conte/poster"
              />
            </div>
            <span className="text-xs text-[#9CA3AF] font-mono mt-3">Format Vertical TikTok/Reels 1080×1920</span>
          </div>

          {/* Kits Réseaux Sociaux & Téléchargements */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-[#12141F] border border-[#1E2235] rounded-xl p-5 space-y-4">
              <h3 className="text-base font-semibold text-[#F4C542] flex items-center gap-2">
                <Download size={18} />
                Exportations Multi-Formats
              </h3>
              <div className="grid grid-cols-3 gap-3">
                <a href={`/api/media/${storyId}/video`} download className="p-3 bg-[#0D0E15] hover:bg-[#1E2235] border border-[#1E2235] rounded-lg text-center transition">
                  <span className="text-xs font-bold block text-white">9:16 Vertical</span>
                  <span className="text-[10px] text-[#9CA3AF]">TikTok / Reels</span>
                </a>
                <a href={`/api/media/${storyId}/subtitles/srt`} download className="p-3 bg-[#0D0E15] hover:bg-[#1E2235] border border-[#1E2235] rounded-lg text-center transition">
                  <span className="text-xs font-bold block text-white">Sous-titres .SRT</span>
                  <span className="text-[10px] text-[#9CA3AF]">Format standard</span>
                </a>
                <a href={`/api/media/${storyId}/subtitles/ass`} download className="p-3 bg-[#0D0E15] hover:bg-[#1E2235] border border-[#1E2235] rounded-lg text-center transition">
                  <span className="text-xs font-bold block text-white">Cinétique .ASS</span>
                  <span className="text-[10px] text-[#9CA3AF]">Styles colorés</span>
                </a>
              </div>
            </div>

            {/* Social Kit SEO */}
            {socialData && (
              <div className="bg-[#12141F] border border-[#1E2235] rounded-xl p-5 space-y-4">
                <h3 className="text-base font-semibold text-[#F4C542] flex items-center gap-2">
                  <Share2 size={18} />
                  Social Media Kit (TikTok & YouTube SEO)
                </h3>
                
                <div className="space-y-3 text-xs">
                  <div>
                    <span className="text-[#9CA3AF] block mb-1">🎯 Accroche des 3 premières secondes (Hook) :</span>
                    <div className="bg-[#0D0E15] p-2.5 rounded text-white font-medium">{socialData.tiktok?.hook_phrase}</div>
                  </div>
                  <div>
                    <span className="text-[#9CA3AF] block mb-1">🔥 Titre Viral & Hashtags TikTok :</span>
                    <div className="bg-[#0D0E15] p-2.5 rounded text-[#CBD5E1]">
                      {socialData.tiktok?.viral_title} — {socialData.tiktok?.hashtags?.join(' ')}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 6. AUDIT & MANIFEST */}
      {activeTab === 'manifest' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-bold text-[#F4C542] flex items-center gap-2">
              <Layers size={20} />
              Render Manifest & Journal d'Audit JSONL
            </h2>
            <span className="text-xs text-[#9CA3AF] font-mono">
              Événements : {manifestEvents.length}
            </span>
          </div>

          <div className="bg-[#0D0E15] border border-[#1E2235] rounded-xl p-4 font-mono text-xs max-h-[500px] overflow-y-auto space-y-2">
            {manifestEvents.map((ev, i) => (
              <div key={i} className="p-2.5 rounded bg-[#12141F] border border-[#1E2235]/60 flex justify-between items-start gap-4">
                <div>
                  <span className="text-amber-400 font-bold">[{ev.step.toUpperCase()}]</span>{' '}
                  <span className="text-white">{ev.action}</span>
                  <p className="text-[11px] text-[#9CA3AF] mt-1">{JSON.stringify(ev.details)}</p>
                </div>
                <span className="text-[10px] text-[#6B7280] shrink-0">{ev.timestamp}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
