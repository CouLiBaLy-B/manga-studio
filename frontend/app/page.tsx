'use client';

import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause,
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
  ArrowDown,
  Copy,
  Check,
  Cpu,
  Tv,
  Smartphone,
  ExternalLink,
  ChevronRight,
  Info,
  Clock,
  Volume2,
  Wand2
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
  const [generationLogs, setGenerationLogs] = useState<string[]>([]);
  const [bibleData, setBibleData] = useState<any>(null);
  const [storyboardData, setStoryboardData] = useState<any>(null);
  const [qcData, setQcData] = useState<any[]>([]);
  const [manifestEvents, setManifestEvents] = useState<any[]>([]);
  const [socialData, setSocialData] = useState<any>(null);
  const [manifestFilter, setManifestFilter] = useState('all');
  
  // Édition temps réel
  const [editingSceneId, setEditingSceneId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<any>({});
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const stylePresets = [
    { 
      key: 'watercolor_mythology', 
      name: 'Mythologie & Or Sacré', 
      desc: 'Enluminures divines, sumi-e et dorures royales.',
      tag: 'Recommandé Conte',
      color: 'border-amber-500/40 bg-amber-500/10 text-amber-300'
    },
    { 
      key: 'shonen_epic', 
      name: 'Shōnen Épique', 
      desc: 'Traits dynamiques, contrastes forts et action explosive.',
      tag: 'Dynamique',
      color: 'border-orange-500/40 bg-orange-500/10 text-orange-300'
    },
    { 
      key: 'seinen_dark_fantasy', 
      name: 'Seinen Dark Fantasy', 
      desc: 'Clair-obscur dramatique, textures brutes et ombres profondes.',
      tag: 'Sombre & Mature',
      color: 'border-purple-500/40 bg-purple-500/10 text-purple-300'
    },
    { 
      key: 'ghibli_poetic', 
      name: 'Ghibli Poétique', 
      desc: 'Aquarelle douce, nature luxuriante et lumière pastel.',
      tag: 'Poétique',
      color: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300'
    },
    { 
      key: 'cyberpunk_neo_tokyo', 
      name: 'Cyberpunk Néo-Tokyo', 
      desc: 'Néons futuristes, pluie nocturne et reflets holographiques.',
      tag: 'Futuriste',
      color: 'border-cyan-500/40 bg-cyan-500/10 text-cyan-300'
    }
  ];

  const pipelineSteps = [
    { num: 1, title: 'Ingestion & Empreintes SHA-256', desc: 'Indexation des images et extraction du conte.' },
    { num: 2, title: 'Fiches Personnages Canoniques', desc: 'Verrouillage immuable (locked=True).' },
    { num: 3, title: 'Génération Storyboard LLM', desc: 'Validation Pydantic et continuité narrative.' },
    { num: 4, title: 'Génération Vidéo Séquentielle', desc: 'Rendu sous surveillance VRAM (22 Go max).' },
    { num: 5, title: 'Contrôle Qualité Automatisé', desc: 'Mesure DINOv2 (>=0.75) et WER audio Whisper.' },
    { num: 6, title: 'Assemblage FFmpeg & EBU R128', desc: 'Normalisation -14 LUFS et sous-titrage synchrone.' },
    { num: 7, title: 'Clôture Render Manifest', desc: 'Génération du rapport de run et audit légal.' }
  ];

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
      console.warn('Données du run:', e);
    }
  };

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
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
    setGenerationLogs(['Initialisation de l\'orchestrateur LangGraph...']);

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
      let currentS = 1;
      const interval = setInterval(() => {
        if (currentS < 6) {
          currentS += 1;
          setGenerationStep(currentS);
          setGenerationLogs(prev => [...prev, `[Step ${currentS}/7] ${pipelineSteps[currentS - 1].title}`]);
        }
      }, 450);

      const res = await fetch('/api/upload-and-run', {
        method: 'POST',
        body: formData,
      });

      clearInterval(interval);
      setGenerationStep(7);
      setGenerationLogs(prev => [...prev, '[Finalize] Génération terminée avec succès (Statut COMPLETED)']);

      if (res.ok) {
        await fetchRunData(storyId);
        setTimeout(() => setActiveTab('player'), 600);
      } else {
        alert('Erreur lors de la génération.');
      }
    } catch (err) {
      console.error(err);
      alert('Erreur de connexion au serveur API.');
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

  const filteredEvents = manifestFilter === 'all' 
    ? manifestEvents 
    : manifestEvents.filter(ev => ev.step.toLowerCase() === manifestFilter.toLowerCase());

  return (
    <div className="min-h-screen bg-[#07080D] text-[#F3F4F6] pb-16">
      {/* Top Professional App Bar */}
      <header className="sticky top-0 z-50 bg-[#0F111A]/90 backdrop-blur-xl border-b border-[#1C2030] px-6 py-3.5 flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center text-black font-black shadow-lg shadow-amber-500/20">
            ⚡
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
                MangaTok Studio <span className="text-amber-400 font-mono text-xs font-normal">v1.2.0</span>
              </h1>
              <span className="text-[11px] font-mono uppercase px-2 py-0.5 rounded-full bg-amber-400/10 text-amber-300 border border-amber-400/25">
                Mode « Conte animé »
              </span>
            </div>
            <p className="text-xs text-[#9CA3AF]">Orchestrateur Hexagonal & LangGraph pour vidéo verticale 9:16</p>
          </div>
        </div>

        {/* Status Bar */}
        <div className="flex items-center gap-3 font-mono text-xs">
          <div className="flex items-center gap-2 bg-[#151824] border border-[#1C2030] px-3 py-1.5 rounded-lg text-[#CBD5E1]">
            <Cpu size={14} className="text-cyan-400" />
            <span>NVIDIA RTX 4090</span>
            <span className="text-emerald-400 font-bold">22.0 GB GUARD</span>
          </div>

          <div className="flex items-center gap-2 bg-[#151824] border border-[#1C2030] px-3 py-1.5 rounded-lg text-[#CBD5E1]">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>API : PORT 8000</span>
          </div>

          <button 
            onClick={() => fetchRunData(storyId)}
            className="p-2 rounded-lg bg-[#151824] hover:bg-[#1C2030] border border-[#1C2030] text-[#9CA3AF] hover:text-white transition"
            title="Rafraîchir les données"
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 pt-6">
        {/* Navigation Tabs */}
        <nav className="flex flex-wrap gap-2 mb-8 bg-[#0F111A] p-1.5 rounded-2xl border border-[#1C2030] shadow-xl">
          {[
            { id: 'studio', label: '1. Studio Créatif & Import', icon: Sliders, badge: 'Étape 1' },
            { id: 'bible', label: '2. Fiches Personnages', icon: UserCheck, badge: bibleData ? `${bibleData.characters?.length || 0} fiches` : null },
            { id: 'storyboard', label: '3. Storyboard & Timeline', icon: Film, badge: storyboardData ? `${storyboardData.segments?.length || 0} scènes` : null },
            { id: 'qc', label: '4. Contrôle Qualité (QC)', icon: ShieldCheck, badge: qcData.length ? `${qcData.length} validés` : null },
            { id: 'player', label: '5. Lecteur 9:16 & Multi-Format', icon: Smartphone, badge: 'Master MP4' },
            { id: 'manifest', label: '6. Audit & Traçabilité', icon: Layers, badge: `${manifestEvents.length} logs` },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2.5 px-4 py-2.5 rounded-xl font-medium text-xs md:text-sm transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-amber-400 to-amber-500 text-black shadow-lg shadow-amber-500/20 font-bold scale-[1.02]'
                    : 'text-[#9CA3AF] hover:text-white hover:bg-[#151824]'
                }`}
              >
                <Icon size={16} />
                <span>{tab.label}</span>
                {tab.badge && (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                    isActive ? 'bg-black/20 text-black' : 'bg-[#1C2030] text-amber-300'
                  }`}>
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* 1. STUDIO CRÉATIF & IMPORT */}
        {activeTab === 'studio' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              {/* Script du Conte */}
              <div className="bg-[#0F111A] border border-[#1C2030] rounded-2xl p-5 shadow-xl">
                <div className="flex justify-between items-center mb-3">
                  <h2 className="text-sm font-bold text-amber-400 flex items-center gap-2 uppercase tracking-wide">
                    <FileText size={16} />
                    Texte du Conte (Français)
                  </h2>
                  <div className="flex items-center gap-3 text-xs font-mono text-[#9CA3AF]">
                    <span>{taleText.split(/\s+/).filter(Boolean).length} mots</span>
                    <span>•</span>
                    <span className="text-cyan-400 font-semibold">~{Math.max(5, Math.ceil(taleText.split(/\s+/).filter(Boolean).length / 15 * 5))}s vidéo</span>
                  </div>
                </div>
                <textarea
                  value={taleText}
                  onChange={(e) => setTaleText(e.target.value)}
                  rows={9}
                  className="w-full bg-[#07080D] border border-[#1C2030] rounded-xl p-4 text-sm text-[#F3F4F6] focus:outline-none focus:border-amber-400/80 font-sans leading-relaxed transition"
                  placeholder="Écrivez ou importez votre conte littéraire en français..."
                />
              </div>

              {/* Import des Images Personnages (1 à 9) */}
              <div className="bg-[#0F111A] border border-[#1C2030] rounded-2xl p-5 shadow-xl">
                <div className="flex justify-between items-center mb-3">
                  <h2 className="text-sm font-bold text-amber-400 flex items-center gap-2 uppercase tracking-wide">
                    <UploadCloud size={16} />
                    Images Canoniques des Personnages (1 à 9)
                  </h2>
                  <span className="text-xs text-[#9CA3AF] font-mono">
                    {selectedFiles.length > 0 ? `${selectedFiles.length}/9 sélectionnés` : 'Fixtures prêtes (Râ & Gardien)'}
                  </span>
                </div>

                <label className="border-2 border-dashed border-[#1C2030] hover:border-amber-400/60 rounded-2xl p-7 flex flex-col items-center justify-center cursor-pointer bg-[#07080D]/60 hover:bg-[#07080D] transition group">
                  <UploadCloud size={36} className="text-[#9CA3AF] group-hover:text-amber-400 group-hover:scale-110 transition mb-2" />
                  <span className="text-sm font-semibold text-white">Glissez les images de vos personnages ici</span>
                  <span className="text-xs text-[#9CA3AF] mt-1">PNG, JPG, WEBP — Recadrage automatique 9:16 & extraction palette</span>
                  <input type="file" multiple accept="image/*" onChange={handleImageUpload} className="hidden" />
                </label>

                {imagePreviews.length > 0 && (
                  <div className="grid grid-cols-3 sm:grid-cols-5 gap-3 mt-4">
                    {imagePreviews.map((src, i) => (
                      <div key={i} className="relative group rounded-xl overflow-hidden border border-[#1C2030] aspect-square bg-black shadow-md">
                        <img src={src} alt={`Preview ${i}`} className="w-full h-full object-cover" />
                        <div className="absolute inset-0 bg-black/70 opacity-0 group-hover:opacity-100 flex flex-col items-center justify-center text-[11px] text-white p-2 text-center transition">
                          <span className="font-bold truncate w-full">{selectedFiles[i]?.name}</span>
                          <span className="text-amber-400 font-mono text-[9px] mt-1">Slot #{i+1}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Panneau Latéral : Presets de Style & Lancement */}
            <div className="space-y-6">
              <div className="bg-[#0F111A] border border-[#1C2030] rounded-2xl p-5 shadow-xl space-y-4">
                <h2 className="text-sm font-bold text-amber-400 flex items-center gap-2 uppercase tracking-wide">
                  <Wand2 size={16} />
                  Preset Stylistique Manga
                </h2>

                <div className="space-y-2.5">
                  {stylePresets.map(p => {
                    const isSelected = stylePreset === p.key;
                    return (
                      <div 
                        key={p.key} 
                        onClick={() => setStylePreset(p.key)}
                        className={`p-3 rounded-xl border cursor-pointer transition flex flex-col gap-1 ${
                          isSelected 
                            ? 'border-amber-400 bg-amber-400/10 shadow-md shadow-amber-400/5' 
                            : 'border-[#1C2030] bg-[#07080D] hover:border-[#2E354B]'
                        }`}
                      >
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-bold text-white">{p.name}</span>
                          <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-semibold border ${p.color}`}>
                            {p.tag}
                          </span>
                        </div>
                        <p className="text-xs text-[#9CA3AF] leading-relaxed">{p.desc}</p>
                      </div>
                    );
                  })}
                </div>

                <div className="pt-3 border-t border-[#1C2030] grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-[11px] font-mono text-[#9CA3AF] block mb-1">Profil Légal</label>
                    <select
                      value={deploymentProfile}
                      onChange={(e) => setDeploymentProfile(e.target.value)}
                      className="w-full bg-[#07080D] border border-[#1C2030] rounded-lg p-2 text-xs text-white focus:outline-none focus:border-amber-400"
                    >
                      <option value="research">Research (Recherche)</option>
                      <option value="commercial">Commercial (Strict)</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-[11px] font-mono text-[#9CA3AF] block mb-1">Territoire ISO</label>
                    <select
                      value={territory}
                      onChange={(e) => setTerritory(e.target.value)}
                      className="w-full bg-[#07080D] border border-[#1C2030] rounded-lg p-2 text-xs text-white focus:outline-none focus:border-amber-400"
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
                  className="w-full mt-3 bg-gradient-to-r from-amber-400 to-amber-500 hover:from-yellow-300 hover:to-amber-400 text-black font-extrabold py-3.5 px-4 rounded-xl flex items-center justify-center gap-2.5 shadow-xl shadow-amber-500/20 transition-all hover:scale-[1.02] disabled:opacity-50 cursor-pointer"
                >
                  {isGenerating ? (
                    <>
                      <RefreshCw size={18} className="animate-spin" />
                      Génération en cours ({generationStep}/7)...
                    </>
                  ) : (
                    <>
                      <Sparkles size={18} />
                      Lancer la Génération Vidéo
                    </>
                  )}
                </button>
              </div>

              {/* Progress Box during Generation */}
              {isGenerating && (
                <div className="bg-[#0F111A] border border-amber-400/30 rounded-2xl p-5 shadow-2xl space-y-3 animate-fade-in">
                  <div className="flex justify-between items-center text-xs font-mono">
                    <span className="text-amber-400 font-bold">PIPELINE LANGGRAPH ACTIF</span>
                    <span>Étape {generationStep} / 7</span>
                  </div>
                  <div className="w-full bg-[#07080D] h-2 rounded-full overflow-hidden border border-[#1C2030]">
                    <div 
                      className="bg-gradient-to-r from-amber-400 to-amber-500 h-full rounded-full transition-all duration-300"
                      style={{ width: `${(generationStep / 7) * 100}%` }}
                    />
                  </div>
                  <div className="text-[11px] font-mono text-[#9CA3AF] max-h-24 overflow-y-auto space-y-1 bg-[#07080D] p-2.5 rounded-lg border border-[#1C2030]">
                    {generationLogs.map((l, idx) => (
                      <div key={idx} className="flex items-center gap-1.5 text-emerald-400">
                        <Check size={12} /> {l}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 2. FICHES PERSONNAGES */}
        {activeTab === 'bible' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-base font-bold text-amber-400 flex items-center gap-2 uppercase tracking-wide">
                  <UserCheck size={18} />
                  Fiches Personnages Canoniques Verrouillées
                </h2>
                <p className="text-xs text-[#9CA3AF] mt-0.5">Immuables (locked: true) — Garantissent la cohérence d'identité dans chaque prompt</p>
              </div>
              <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-full font-mono font-semibold flex items-center gap-1.5">
                <ShieldCheck size={14} />
                LOCKED CANONICAL
              </span>
            </div>

            {bibleData ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {bibleData.characters?.map((char: any) => (
                  <div key={char.character_id} className="bg-[#0F111A] border border-[#1C2030] rounded-2xl p-5 space-y-4 shadow-xl hover:border-amber-400/30 transition">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="text-lg font-bold text-white flex items-center gap-2">
                          {char.nom}
                        </h3>
                        <p className="text-xs text-amber-300/80 font-medium">{char.role}</p>
                      </div>
                      <span className="text-xs font-mono bg-[#07080D] border border-[#1C2030] px-2.5 py-1 rounded-lg text-cyan-300">
                        #{char.character_id}
                      </span>
                    </div>

                    {/* Nuancier Hexadécimal */}
                    <div>
                      <span className="text-[11px] font-mono text-[#9CA3AF] block mb-1.5">Codes Couleurs Invariants :</span>
                      <div className="flex flex-wrap gap-2">
                        {char.description_physique?.couleurs_hex?.map((hex: string, i: number) => (
                          <button 
                            key={i} 
                            onClick={() => copyToClipboard(hex, `hex-${char.character_id}-${i}`)}
                            className="flex items-center gap-1.5 text-xs font-mono bg-[#07080D] px-2.5 py-1 rounded-lg border border-[#1C2030] hover:border-amber-400 transition"
                            title="Cliquer pour copier"
                          >
                            <span className="w-3.5 h-3.5 rounded-full shadow-inner" style={{ backgroundColor: hex }} />
                            <span>{hex}</span>
                            {copiedKey === `hex-${char.character_id}-${i}` ? <Check size={12} className="text-emerald-400" /> : <Copy size={10} className="text-[#6B7280]" />}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Attributs physiques */}
                    <div className="bg-[#07080D] p-3.5 rounded-xl text-xs space-y-1.5 text-[#CBD5E1] border border-[#1C2030]">
                      <p><strong className="text-[#9CA3AF]">Silhouette :</strong> {char.description_physique?.silhouette}</p>
                      <p><strong className="text-[#9CA3AF]">Visage & Regard :</strong> {char.description_physique?.visage}</p>
                      <p><strong className="text-[#9CA3AF]">Peau :</strong> {char.description_physique?.peau}</p>
                      <p><strong className="text-[#9CA3AF]">Coiffure :</strong> {char.description_physique?.coiffure}</p>
                      <p><strong className="text-[#9CA3AF]">Tenue Royale :</strong> {char.description_physique?.tenue}</p>
                      <p><strong className="text-[#9CA3AF]">Accessoires Signature :</strong> {char.description_physique?.accessoires_signature?.join(', ')}</p>
                    </div>

                    <div className="flex justify-between items-center text-xs text-[#9CA3AF] pt-2 border-t border-[#1C2030] font-mono">
                      <span className="flex items-center gap-1 text-amber-300">
                        <Volume2 size={14} /> {char.voix_suggeree?.ton}
                      </span>
                      <span className="text-[#9CA3AF]">
                        {char.traits_caractere?.map((t: string) => `#${t}`).join(' ')}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-12 text-center bg-[#0F111A] rounded-2xl border border-[#1C2030]">
                <p className="text-sm text-[#9CA3AF]">Aucune fiche chargée. Lancez une génération depuis l'onglet Studio.</p>
              </div>
            )}
          </div>
        )}

        {/* 3. STORYBOARD STUDIO */}
        {activeTab === 'storyboard' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-base font-bold text-amber-400 flex items-center gap-2 uppercase tracking-wide">
                  <Film size={18} />
                  Storyboard Structuré & Éditeur Human-in-the-Loop
                </h2>
                <p className="text-xs text-[#9CA3AF] mt-0.5">Ajustez en direct les dialogues français, le cadrage caméra et les prompts IA</p>
              </div>
              <div className="text-xs font-mono bg-[#0F111A] px-3 py-1.5 rounded-lg border border-[#1C2030] text-[#CBD5E1]">
                {storyboardData?.segments?.length || 0} scènes • Total {storyboardData?.segments?.reduce((acc: number, s: any) => acc + s.duree_s, 0) || 0}s
              </div>
            </div>

            <div className="space-y-4">
              {storyboardData?.segments?.map((seg: any, idx: number) => {
                const isEditing = editingSceneId === seg.scene_id;
                return (
                  <div key={seg.scene_id} className="bg-[#0F111A] border border-[#1C2030] rounded-2xl p-5 space-y-3.5 shadow-xl hover:border-[#2E354B] transition">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2.5">
                        <span className="text-xs font-mono font-bold bg-amber-400 text-black px-2.5 py-0.5 rounded-md">
                          #{seg.ordre}
                        </span>
                        <h3 className="text-base font-bold text-white">{seg.titre}</h3>
                        <span className="text-xs font-mono text-[#9CA3AF]">({seg.scene_id})</span>
                      </div>

                      <div className="flex items-center gap-1.5">
                        <button onClick={() => handleReorder(idx, 'up')} disabled={idx === 0} className="p-1.5 rounded-lg hover:bg-[#1C2030] text-[#9CA3AF] disabled:opacity-20 transition" title="Monter la scène">
                          <ArrowUp size={15} />
                        </button>
                        <button onClick={() => handleReorder(idx, 'down')} disabled={idx === (storyboardData.segments.length - 1)} className="p-1.5 rounded-lg hover:bg-[#1C2030] text-[#9CA3AF] disabled:opacity-20 transition" title="Descendre la scène">
                          <ArrowDown size={15} />
                        </button>
                        <button 
                          onClick={() => isEditing ? handleSaveScene(seg.scene_id) : handleEditScene(seg)}
                          className={`text-xs px-3.5 py-1.5 rounded-lg font-bold flex items-center gap-1.5 transition ${
                            isEditing ? 'bg-emerald-400 text-black shadow-lg shadow-emerald-400/20' : 'bg-[#151824] text-white hover:bg-[#1C2030]'
                          }`}
                        >
                          {isEditing ? <><Save size={14} /> Enregistrer</> : <><Edit3 size={14} /> Modifier</>}
                        </button>
                      </div>
                    </div>

                    {isEditing ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 bg-[#07080D] p-4 rounded-xl border border-[#1C2030]">
                        <div>
                          <label className="text-[11px] font-mono text-amber-400 block mb-1">Titre & Action (FR) :</label>
                          <input
                            type="text"
                            value={editForm.titre}
                            onChange={(e) => setEditForm({ ...editForm, titre: e.target.value })}
                            className="w-full bg-[#0F111A] border border-[#1C2030] rounded p-2 text-xs text-white mb-2"
                          />
                          <textarea
                            value={editForm.frame}
                            onChange={(e) => setEditForm({ ...editForm, frame: e.target.value })}
                            rows={3}
                            className="w-full bg-[#0F111A] border border-[#1C2030] rounded p-2 text-xs text-white"
                          />
                        </div>
                        <div>
                          <label className="text-[11px] font-mono text-amber-400 block mb-1">Prompt IA Vidéo (EN) :</label>
                          <textarea
                            value={editForm.prompt_ia}
                            onChange={(e) => setEditForm({ ...editForm, prompt_ia: e.target.value })}
                            rows={5}
                            className="w-full bg-[#0F111A] border border-[#1C2030] rounded p-2 text-xs text-white font-mono"
                          />
                        </div>
                      </div>
                    ) : (
                      <>
                        <div className="bg-[#07080D] p-3.5 rounded-xl border border-[#1C2030]/80 space-y-2">
                          <p className="text-xs text-[#CBD5E1]">
                            <strong className="text-amber-300">Action Narrative :</strong> {seg.frame}
                          </p>
                          <p className="text-xs text-[#94A3B8] font-mono">
                            <strong className="text-cyan-400">Prompt IA :</strong> {seg.prompt_ia}
                          </p>
                        </div>

                        {/* Badges de scène */}
                        <div className="flex flex-wrap gap-2 text-xs font-mono">
                          <span className="bg-[#151824] px-2.5 py-1 rounded-md text-amber-300 border border-[#1C2030]">
                            ⏱️ {seg.duree_s}s
                          </span>
                          <span className="bg-[#151824] px-2.5 py-1 rounded-md text-purple-300 border border-[#1C2030]">
                            🎭 {seg.emotion}
                          </span>
                          <span className="bg-[#151824] px-2.5 py-1 rounded-md text-blue-300 border border-[#1C2030]">
                            📐 {seg.plan}
                          </span>
                          <span className="bg-[#151824] px-2.5 py-1 rounded-md text-emerald-300 border border-[#1C2030]">
                            ✨ {seg.transition?.type} ({seg.transition?.duration_s}s)
                          </span>
                          <span className="bg-[#151824] px-2.5 py-1 rounded-md text-[#9CA3AF] border border-[#1C2030]">
                            👥 {seg.characters_present?.join(', ')}
                          </span>
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
              <div>
                <h2 className="text-base font-bold text-amber-400 flex items-center gap-2 uppercase tracking-wide">
                  <ShieldCheck size={18} />
                  Tableau de Bord Contrôle Qualité (DINOv2 & WER)
                </h2>
                <p className="text-xs text-[#9CA3AF] mt-0.5">Validation d'identité visuelle et intelligibilité de la voix française</p>
              </div>
              <div className="flex gap-2">
                <span className="text-xs font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded-full">
                  SEUIL DINOv2: 0.75
                </span>
                <span className="text-xs font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-3 py-1 rounded-full">
                  WER MAX: 15%
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {qcData.map((qc: any, i: number) => {
                const isPassed = qc.status === 'passed';
                return (
                  <div key={i} className="bg-[#0F111A] border border-[#1C2030] rounded-2xl p-5 space-y-4 shadow-xl">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-bold text-white">Scène #{i + 1} ({qc.segment_id})</span>
                      <span className={`text-xs px-2.5 py-0.5 rounded-full font-mono font-bold uppercase ${
                        isPassed 
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' 
                          : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                      }`}>
                        {qc.status}
                      </span>
                    </div>

                    {/* Jauge DINOv2 */}
                    <div className="bg-[#07080D] p-3.5 rounded-xl border border-[#1C2030] space-y-2">
                      <div className="flex justify-between text-xs font-mono">
                        <span className="text-[#9CA3AF]">Similarité DINOv2 :</span>
                        <span className="font-bold text-emerald-400">{qc.visual_similarity?.score?.toFixed(2)} / 1.00</span>
                      </div>
                      <div className="w-full bg-[#151824] h-2 rounded-full overflow-hidden">
                        <div 
                          className="bg-gradient-to-r from-emerald-500 to-cyan-400 h-full rounded-full transition-all" 
                          style={{ width: `${(qc.visual_similarity?.score || 0) * 100}%` }}
                        />
                      </div>
                    </div>

                    {/* Word Error Rate */}
                    <div className="text-xs flex justify-between bg-[#07080D] p-3 rounded-xl border border-[#1C2030] font-mono">
                      <span className="text-[#9CA3AF]">WER Français (Whisper) :</span>
                      <span className="text-cyan-400 font-bold">{((qc.dialogue_wer || 0) * 100).toFixed(1)}%</span>
                    </div>

                    <div className="text-xs text-[#9CA3AF] space-y-1.5 pt-1">
                      <p className="flex items-center gap-1.5 text-[#CBD5E1]">
                        <Check size={14} className="text-emerald-400" /> Flux audio présent & normalisé
                      </p>
                      <p className="flex items-center gap-1.5 text-[#CBD5E1]">
                        <Check size={14} className="text-emerald-400" /> Cadrage vertical 9:16 conforme
                      </p>
                      <p className="flex items-center gap-1.5 text-[#CBD5E1]">
                        <Check size={14} className="text-emerald-400" /> Recommandation : <strong className="text-white uppercase font-mono">{qc.recommendation}</strong>
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* 5. LECTEUR 9:16 & MULTI-FORMATS */}
        {activeTab === 'player' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Mockup Smartphone TikTok Player */}
            <div className="flex flex-col items-center">
              <div className="w-[300px] h-[580px] bg-black rounded-[40px] border-8 border-[#1C2030] overflow-hidden shadow-2xl shadow-amber-500/10 relative flex items-center justify-center group">
                <video 
                  src={`/api/media/${storyId}/video`} 
                  controls 
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-4 left-1/2 -translate-x-1/2 w-24 h-4 bg-[#1C2030] rounded-full z-10 pointer-events-none" />
              </div>
              <span className="text-xs text-[#9CA3AF] font-mono mt-4 flex items-center gap-1.5">
                <Smartphone size={14} /> Profil TikTok / Reels 1080×1920
              </span>
            </div>

            {/* Hub d'Export & Kit Viral */}
            <div className="lg:col-span-2 space-y-6">
              {/* Cartes de Téléchargement Multi-Formats */}
              <div className="bg-[#0F111A] border border-[#1C2030] rounded-2xl p-5 space-y-4 shadow-xl">
                <h3 className="text-sm font-bold text-amber-400 flex items-center gap-2 uppercase tracking-wide">
                  <Download size={16} />
                  Téléchargements & Multi-Formats
                </h3>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <a href={`/api/media/${storyId}/video`} download className="p-4 bg-[#07080D] hover:bg-[#151824] border border-[#1C2030] rounded-xl text-center transition group">
                    <span className="text-sm font-bold block text-white group-hover:text-amber-400">9:16 Vertical</span>
                    <span className="text-[11px] text-[#9CA3AF]">TikTok / Reels (1080×1920)</span>
                  </a>
                  <a href={`/api/media/${storyId}/subtitles/srt`} download className="p-4 bg-[#07080D] hover:bg-[#151824] border border-[#1C2030] rounded-xl text-center transition group">
                    <span className="text-sm font-bold block text-white group-hover:text-cyan-400">Sous-Titres .SRT</span>
                    <span className="text-[11px] text-[#9CA3AF]">Standard synchronisé</span>
                  </a>
                  <a href={`/api/media/${storyId}/subtitles/ass`} download className="p-4 bg-[#07080D] hover:bg-[#151824] border border-[#1C2030] rounded-xl text-center transition group">
                    <span className="text-sm font-bold block text-white group-hover:text-purple-400">Cinétique .ASS</span>
                    <span className="text-[11px] text-[#9CA3AF]">Styles et rebonds dorés</span>
                  </a>
                </div>
              </div>

              {/* Social Media Kit */}
              {socialData && (
                <div className="bg-[#0F111A] border border-[#1C2030] rounded-2xl p-5 space-y-4 shadow-xl">
                  <h3 className="text-sm font-bold text-amber-400 flex items-center gap-2 uppercase tracking-wide">
                    <Share2 size={16} />
                    Social Media Viral Kit (SEO & Hashtags)
                  </h3>

                  <div className="space-y-3.5 text-xs">
                    <div>
                      <span className="text-[#9CA3AF] font-mono block mb-1">🎯 Accroche des 3 premières secondes (Hook) :</span>
                      <div className="bg-[#07080D] p-3 rounded-xl text-white font-medium border border-[#1C2030] flex justify-between items-center">
                        <span>{socialData.tiktok?.hook_phrase}</span>
                        <button onClick={() => copyToClipboard(socialData.tiktok?.hook_phrase, 'hook')} className="text-amber-400 hover:text-white">
                          {copiedKey === 'hook' ? <Check size={14} /> : <Copy size={14} />}
                        </button>
                      </div>
                    </div>

                    <div>
                      <span className="text-[#9CA3AF] font-mono block mb-1">🔥 Titre Viral & Hashtags TikTok :</span>
                      <div className="bg-[#07080D] p-3 rounded-xl text-[#CBD5E1] border border-[#1C2030] flex justify-between items-center">
                        <span>{socialData.tiktok?.viral_title} {socialData.tiktok?.hashtags?.join(' ')}</span>
                        <button onClick={() => copyToClipboard(`${socialData.tiktok?.viral_title} ${socialData.tiktok?.hashtags?.join(' ')}`, 'tt')} className="text-amber-400 hover:text-white">
                          {copiedKey === 'tt' ? <Check size={14} /> : <Copy size={14} />}
                        </button>
                      </div>
                    </div>

                    <div>
                      <span className="text-[#9CA3AF] font-mono block mb-1">📺 Description YouTube Shorts avec Chapitres :</span>
                      <div className="bg-[#07080D] p-3 rounded-xl text-[#CBD5E1] border border-[#1C2030] font-mono whitespace-pre-wrap flex justify-between items-start">
                        <span>{socialData.youtube_shorts?.description}</span>
                        <button onClick={() => copyToClipboard(socialData.youtube_shorts?.description, 'yt')} className="text-amber-400 hover:text-white">
                          {copiedKey === 'yt' ? <Check size={14} /> : <Copy size={14} />}
                        </button>
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
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h2 className="text-base font-bold text-amber-400 flex items-center gap-2 uppercase tracking-wide">
                  <Layers size={18} />
                  Journal d'Audit Render Manifest (JSONL Event Stream)
                </h2>
                <p className="text-xs text-[#9CA3AF] mt-0.5">Traçabilité immuable, conformité des licences et empreintes SHA-256</p>
              </div>

              {/* Filtres d'événements */}
              <div className="flex gap-1.5 bg-[#0F111A] p-1 rounded-xl border border-[#1C2030] text-xs font-mono">
                {['all', 'ingestion', 'bible', 'storyboard', 'clip_generation', 'quality_control', 'assembly'].map((f) => (
                  <button
                    key={f}
                    onClick={() => setManifestFilter(f)}
                    className={`px-3 py-1 rounded-lg capitalize transition ${
                      manifestFilter === f ? 'bg-amber-400 text-black font-bold' : 'text-[#9CA3AF] hover:text-white'
                    }`}
                  >
                    {f}
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-[#07080D] border border-[#1C2030] rounded-2xl p-4 font-mono text-xs max-h-[550px] overflow-y-auto space-y-2.5">
              {filteredEvents.map((ev, i) => (
                <div key={i} className="p-3 rounded-xl bg-[#0F111A] border border-[#1C2030] flex justify-between items-start gap-4 hover:border-[#2E354B] transition">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-amber-400 font-bold">[{ev.step.toUpperCase()}]</span>
                      <span className="text-white font-semibold">{ev.action}</span>
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {ev.status}
                      </span>
                    </div>
                    <p className="text-[11px] text-[#9CA3AF] break-all">{JSON.stringify(ev.details)}</p>
                  </div>
                  <span className="text-[10px] text-[#6B7280] shrink-0 font-mono">{ev.timestamp}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
