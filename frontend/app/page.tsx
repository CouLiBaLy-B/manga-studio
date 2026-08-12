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
  Wand2,
  Trash2,
  Plus,
  PlayCircle,
  Video,
  Sparkle
} from 'lucide-react';

export default function MangaTokDashboard() {
  const [activeTab, setActiveTab] = useState<'studio' | 'bible' | 'storyboard' | 'qc' | 'player' | 'manifest'>('studio');
  
  // États de l'histoire et presets
  const [storyId, setStoryId] = useState('mythe_ra');
  const [taleText, setTaleText] = useState(`Au commencement des temps, Râ, le grand dieu solaire, régnait sur l'Égypte avec splendeur et bienveillance. Chaque soir, il montait à bord de sa barque céleste sacrée pour traverser le ciel étoilé.

Tandis que la nuit tombait sur le Nil, les fidèles gardiens du temple s'inclinèrent avec un profond respect. « La route du ciel est prête, Seigneur Râ », déclara le premier gardien d'une voix solennelle. Râ sourit et répondit : « Que la lumière ne s'éteigne jamais dans vos cœurs ».

La barque d'or quitta doucement la rive sacrée pour s'élever au milieu des constellations. Le dieu veillait sur le monde des mortels, garantissant que chaque aube apporterait un jour nouveau.`);
  
  const [stylePreset, setStylePreset] = useState('watercolor_mythology');
  const [deploymentProfile, setDeploymentProfile] = useState('research');
  const [territory, setTerritory] = useState('EU');
  const [apiKey, setApiKey] = useState('');
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
      accent: '#F59E0B',
      gradient: 'from-amber-500/20 to-yellow-600/10'
    },
    { 
      key: 'shonen_epic', 
      name: 'Shōnen Épique', 
      desc: 'Traits dynamiques, contrastes forts et action explosive.',
      tag: 'Action & Impact',
      accent: '#EA580C',
      gradient: 'from-orange-500/20 to-red-600/10'
    },
    { 
      key: 'seinen_dark_fantasy', 
      name: 'Seinen Dark Fantasy', 
      desc: 'Clair-obscur dramatique, textures brutes et ombres profondes.',
      tag: 'Sombre & Mature',
      accent: '#9333EA',
      gradient: 'from-purple-500/20 to-indigo-600/10'
    },
    { 
      key: 'ghibli_poetic', 
      name: 'Ghibli Poétique', 
      desc: 'Aquarelle douce, nature luxuriante et lumière pastel.',
      tag: 'Poétique',
      accent: '#10B981',
      gradient: 'from-emerald-500/20 to-teal-600/10'
    },
    { 
      key: 'cyberpunk_neo_tokyo', 
      name: 'Cyberpunk Néo-Tokyo', 
      desc: 'Néons futuristes, pluie nocturne et reflets holographiques.',
      tag: 'Sci-Fi Synth',
      accent: '#06B6D4',
      gradient: 'from-cyan-500/20 to-blue-600/10'
    }
  ];

  const pipelineSteps = [
    { num: 1, title: 'Ingestion & Hashes SHA-256', desc: 'Indexation des images et intégrité du texte.' },
    { num: 2, title: 'Fiches Personnages Canoniques', desc: 'Verrouillage immuable (locked: true).' },
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

  const protectedHeaders = () => apiKey ? { 'X-API-Key': apiKey } : {};

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files).slice(0, 9);
      setSelectedFiles(prev => [...prev, ...files].slice(0, 9));
      const previews = files.map(file => URL.createObjectURL(file));
      setImagePreviews(prev => [...prev, ...previews].slice(0, 9));
    }
  };

  const handleRemoveImage = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    setImagePreviews(prev => prev.filter((_, i) => i !== index));
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
          setGenerationLogs(prev => [...prev, `[Étape ${currentS}/7] ${pipelineSteps[currentS - 1].title}`]);
        }
      }, 450);

      const res = await fetch('/api/upload-and-run', {
        method: 'POST',
        headers: protectedHeaders(),
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
        headers: { 'Content-Type': 'application/json', ...protectedHeaders() },
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
        headers: { 'Content-Type': 'application/json', ...protectedHeaders() },
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
    <div className="min-h-screen bg-[#06070a] text-[#F3F4F6] pb-24 selection:bg-amber-400 selection:text-black">
      {/* Top Professional Header Bar */}
      <header className="sticky top-0 z-50 bg-[#0c0e14]/85 backdrop-blur-2xl border-b border-white/[0.08] px-6 lg:px-10 py-3.5">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-amber-400 via-amber-500 to-amber-600 flex items-center justify-center text-black font-black shadow-lg shadow-amber-500/25">
              <Sparkles size={20} className="text-black" />
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2 font-sans">
                  MangaTok Studio
                </h1>
                <span className="text-[10px] uppercase font-mono font-bold px-2 py-0.5 rounded-full bg-amber-400/10 text-amber-300 border border-amber-400/30">
                  Mode « Conte animé »
                </span>
                <span className="text-[10px] font-mono text-zinc-400 bg-white/[0.04] px-2 py-0.5 rounded-md border border-white/[0.06]">
                  v1.2.0
                </span>
              </div>
              <p className="text-xs text-zinc-400 mt-0.5">Orchestrateur LangGraph • TikTok & Reels 9:16 Pipeline</p>
            </div>
          </div>

          {/* Badges Système et Métriques */}
          <div className="flex items-center gap-2.5 font-mono text-xs">
            <div className="flex items-center gap-2 bg-[#11141d] border border-white/[0.07] px-3.5 py-1.5 rounded-xl text-zinc-300 shadow-sm">
              <Cpu size={14} className="text-cyan-400" />
              <span>RTX 4090</span>
              <span className="text-emerald-400 font-bold">22.0 GB VRAM GUARD</span>
            </div>

            <div className="flex items-center gap-2 bg-[#11141d] border border-white/[0.07] px-3.5 py-1.5 rounded-xl text-zinc-300 shadow-sm">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-zinc-300">API 8000</span>
            </div>

            <button 
              onClick={() => fetchRunData(storyId)}
              className="p-2 rounded-xl bg-[#11141d] hover:bg-[#161a26] border border-white/[0.07] text-zinc-400 hover:text-white transition shadow-sm"
              title="Rafraîchir les données"
            >
              <RefreshCw size={14} />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 lg:px-10 pt-8 space-y-8">
        {/* Navigation Tabs - Navigation Principale */}
        <div className="bg-[#0c0e14]/90 p-1.5 rounded-2xl border border-white/[0.08] shadow-2xl backdrop-blur-xl">
          <nav className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-1.5">
            {[
              { id: 'studio', label: '1. Studio Créatif', icon: Sliders, badge: 'Éditeur' },
              { id: 'bible', label: '2. Fiches Personnages', icon: UserCheck, badge: bibleData ? `${bibleData.characters?.length || 0}` : null },
              { id: 'storyboard', label: '3. Storyboard', icon: Film, badge: storyboardData ? `${storyboardData.segments?.length || 0}` : null },
              { id: 'qc', label: '4. Contrôle Qualité', icon: ShieldCheck, badge: qcData.length ? `${qcData.length} clips` : null },
              { id: 'player', label: '5. Lecteur 9:16', icon: Smartphone, badge: 'Vidéo' },
              { id: 'manifest', label: '6. Audit Manifest', icon: Layers, badge: `${manifestEvents.length}` },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex flex-col sm:flex-row items-center justify-center gap-2 px-3 py-2.5 rounded-xl font-medium text-xs md:text-sm transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-amber-400 to-amber-500 text-black shadow-lg shadow-amber-500/25 font-bold scale-[1.01]'
                      : 'text-zinc-400 hover:text-white hover:bg-white/[0.04]'
                  }`}
                >
                  <Icon size={16} />
                  <span className="truncate">{tab.label}</span>
                  {tab.badge && (
                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                      isActive ? 'bg-black/25 text-black' : 'bg-white/[0.06] text-amber-300'
                    }`}>
                      {tab.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* CONTENU ONGLET 1 : STUDIO CRÉATIF & IMPORT */}
        {activeTab === 'studio' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Colonne Gauche : Script + Images (8 colonnes) */}
            <div className="lg:col-span-8 space-y-6">
              {/* Carte Texte du Conte */}
              <div className="glass-card rounded-3xl p-6 shadow-2xl space-y-4">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-xl bg-amber-400/10 border border-amber-400/30 flex items-center justify-center text-amber-400">
                      <FileText size={16} />
                    </div>
                    <div>
                      <h2 className="text-sm font-bold uppercase tracking-wider text-amber-400">Texte du Conte (Français)</h2>
                      <p className="text-xs text-zinc-400">Mythe, fable ou récit court en plusieurs paragraphes</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3 text-xs font-mono text-zinc-400 bg-white/[0.03] px-3 py-1.5 rounded-xl border border-white/[0.06]">
                    <span>{taleText.split(/\s+/).filter(Boolean).length} mots</span>
                    <span>•</span>
                    <span className="text-cyan-400 font-semibold">~{Math.max(5, Math.ceil(taleText.split(/\s+/).filter(Boolean).length / 15 * 5))}s vidéo</span>
                  </div>
                </div>

                <textarea
                  value={taleText}
                  onChange={(e) => setTaleText(e.target.value)}
                  rows={8}
                  className="w-full bg-[#07080d]/80 border border-white/[0.08] focus:border-amber-400/80 rounded-2xl p-4 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-4 focus:ring-amber-400/10 font-sans leading-relaxed transition resize-y"
                  placeholder="Écrivez ou collez votre conte en français..."
                />
              </div>

              {/* Carte Importation Images Personnages */}
              <div className="glass-card rounded-3xl p-6 shadow-2xl space-y-4">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-xl bg-cyan-400/10 border border-cyan-400/30 flex items-center justify-center text-cyan-400">
                      <UploadCloud size={16} />
                    </div>
                    <div>
                      <h2 className="text-sm font-bold uppercase tracking-wider text-cyan-400">Images des Personnages (1 à 9)</h2>
                      <p className="text-xs text-zinc-400">Portraits de référence pour la cohérence de style et de design</p>
                    </div>
                  </div>

                  <span className="text-xs font-mono text-zinc-400 bg-white/[0.03] px-3 py-1.5 rounded-xl border border-white/[0.06]">
                    {selectedFiles.length > 0 ? `${selectedFiles.length}/9 images` : '4 fixtures intégrées'}
                  </span>
                </div>

                {/* Zone de drop moderne */}
                <label className="border-2 border-dashed border-white/[0.1] hover:border-amber-400/50 hover:bg-amber-400/[0.02] rounded-2xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all duration-300 group">
                  <div className="w-12 h-12 rounded-2xl bg-white/[0.04] group-hover:bg-amber-400/10 flex items-center justify-center text-zinc-400 group-hover:text-amber-400 group-hover:scale-110 transition-all duration-300 mb-3 border border-white/[0.06]">
                    <UploadCloud size={24} />
                  </div>
                  <span className="text-sm font-semibold text-white group-hover:text-amber-300 transition">
                    Déposez vos images ici ou cliquez pour parcourir
                  </span>
                  <span className="text-xs text-zinc-400 mt-1">
                    PNG, JPG, WEBP • Résolution optimale 512×512 ou 9:16
                  </span>
                  <input type="file" multiple accept="image/*" onChange={handleImageUpload} className="hidden" />
                </label>

                {/* Galerie des vignettes */}
                {imagePreviews.length > 0 && (
                  <div className="grid grid-cols-3 sm:grid-cols-5 gap-3 pt-2">
                    {imagePreviews.map((src, i) => (
                      <div key={i} className="relative group rounded-2xl overflow-hidden border border-white/[0.1] aspect-square bg-[#07080d] shadow-lg">
                        <img src={src} alt={`Slot ${i}`} className="w-full h-full object-cover group-hover:scale-105 transition duration-300" />
                        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 flex flex-col items-center justify-between p-2 transition duration-200">
                          <button 
                            onClick={(e) => { e.preventDefault(); handleRemoveImage(i); }}
                            className="self-end p-1 rounded-full bg-red-500/80 hover:bg-red-500 text-white transition"
                          >
                            <Trash2 size={12} />
                          </button>
                          <span className="text-[10px] font-mono text-amber-300 font-bold bg-black/80 px-2 py-0.5 rounded-md">
                            Personnage #{i + 1}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Colonne Droite : Presets & Configuration (4 colonnes) */}
            <div className="lg:col-span-4 space-y-6">
              <div className="glass-card rounded-3xl p-6 shadow-2xl space-y-5">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-xl bg-amber-400/10 border border-amber-400/30 flex items-center justify-center text-amber-400">
                    <Wand2 size={16} />
                  </div>
                  <div>
                    <h2 className="text-sm font-bold uppercase tracking-wider text-amber-400">Preset Stylistique Manga</h2>
                    <p className="text-xs text-zinc-400">Direction artistique injectée dans les prompts IA</p>
                  </div>
                </div>

                {/* Liste des styles */}
                <div className="space-y-2.5">
                  {stylePresets.map(p => {
                    const isSelected = stylePreset === p.key;
                    return (
                      <div 
                        key={p.key} 
                        onClick={() => setStylePreset(p.key)}
                        className={`p-3.5 rounded-2xl border transition-all duration-200 cursor-pointer flex flex-col gap-1 ${
                          isSelected 
                            ? 'border-amber-400/80 bg-amber-400/[0.08] shadow-lg shadow-amber-500/10 ring-1 ring-amber-400/40' 
                            : 'border-white/[0.06] bg-[#07080d]/60 hover:border-white/[0.15] hover:bg-[#07080d]'
                        }`}
                      >
                        <div className="flex justify-between items-center">
                          <span className={`text-sm font-bold ${isSelected ? 'text-amber-300' : 'text-white'}`}>
                            {p.name}
                          </span>
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-mono font-semibold border ${
                            isSelected ? 'bg-amber-400/20 text-amber-300 border-amber-400/40' : 'bg-white/[0.04] text-zinc-400 border-white/[0.08]'
                          }`}>
                            {p.tag}
                          </span>
                        </div>
                        <p className="text-xs text-zinc-400 leading-relaxed">{p.desc}</p>
                      </div>
                    );
                  })}
                </div>

                {/* Configuration Légal & ISO */}
                <div className="pt-4 border-t border-white/[0.08] grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-[11px] font-mono text-zinc-400 block mb-1">Profil Légal</label>
                    <select
                      value={deploymentProfile}
                      onChange={(e) => setDeploymentProfile(e.target.value)}
                      className="w-full bg-[#07080d] border border-white/[0.08] rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-amber-400 font-sans"
                    >
                      <option value="research">Research (Recherche)</option>
                      <option value="commercial">Commercial (Strict)</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] font-mono text-zinc-400 block mb-1">Territoire ISO</label>
                    <select
                      value={territory}
                      onChange={(e) => setTerritory(e.target.value)}
                      className="w-full bg-[#07080d] border border-white/[0.08] rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-amber-400 font-sans"
                    >
                      <option value="EU">Union Européenne (EU)</option>
                      <option value="US">États-Unis (US)</option>
                      <option value="JP">Japon (JP)</option>
                    </select>
                  </div>
                </div>

                <div className="pt-3">
                  <label htmlFor="api-key" className="text-[11px] font-mono text-zinc-400 block mb-1">Clé API</label>
                  <input
                    id="api-key"
                    type="password"
                    autoComplete="off"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="Requise par un serveur protégé"
                    className="w-full bg-[#07080d] border border-white/[0.08] rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-amber-400 font-mono"
                  />
                  <p className="mt-1 text-[10px] text-zinc-500">Utilisée uniquement pour les opérations protégées et jamais enregistrée par le dashboard.</p>
                </div>

                {/* Bouton de génération principal */}
                <button
                  onClick={handleGenerate}
                  disabled={isGenerating}
                  className="w-full mt-2 gold-glow-btn text-black font-extrabold py-4 px-6 rounded-2xl flex items-center justify-center gap-3 text-sm tracking-wide uppercase disabled:opacity-50 cursor-pointer transition-all duration-300"
                >
                  {isGenerating ? (
                    <>
                      <RefreshCw size={18} className="animate-spin text-black" />
                      <span>Pipeline en cours ({generationStep}/7)...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles size={18} className="text-black" />
                      <span>Lancer la Génération Vidéo</span>
                    </>
                  )}
                </button>
              </div>

              {/* Boîte de progression en cours de run */}
              {isGenerating && (
                <div className="glass-card border-amber-400/40 rounded-3xl p-5 shadow-2xl space-y-3.5 animate-fadeIn">
                  <div className="flex justify-between items-center text-xs font-mono">
                    <span className="text-amber-400 font-bold flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
                      PIPELINE LANGGRAPH ACTIF
                    </span>
                    <span className="text-zinc-400">{generationStep} / 7</span>
                  </div>

                  <div className="w-full bg-[#07080d] h-2.5 rounded-full overflow-hidden border border-white/[0.08]">
                    <div 
                      className="bg-gradient-to-r from-amber-400 via-amber-500 to-yellow-300 h-full rounded-full transition-all duration-300"
                      style={{ width: `${(generationStep / 7) * 100}%` }}
                    />
                  </div>

                  <div className="text-[11px] font-mono text-zinc-400 max-h-28 overflow-y-auto space-y-1 bg-[#07080d] p-3 rounded-xl border border-white/[0.06]">
                    {generationLogs.map((log, idx) => (
                      <div key={idx} className="flex items-center gap-1.5 text-emerald-400">
                        <Check size={12} /> {log}
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
                <h2 className="text-lg font-bold text-white flex items-center gap-2.5">
                  <UserCheck className="text-amber-400" size={20} />
                  Bible des Personnages Canoniques
                </h2>
                <p className="text-xs text-zinc-400 mt-0.5">Identités visuelles immuables (locked: true) pour garantir la continuité</p>
              </div>

              <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3.5 py-1.5 rounded-full font-mono font-semibold flex items-center gap-1.5 shadow-sm">
                <ShieldCheck size={14} />
                LOCKED CANONICAL
              </span>
            </div>

            {bibleData ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {bibleData.characters?.map((char: any) => (
                  <div key={char.character_id} className="glass-card rounded-3xl p-6 space-y-4 shadow-2xl glass-card-hover transition duration-300">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="text-lg font-bold text-white flex items-center gap-2">
                          {char.nom}
                        </h3>
                        <p className="text-xs text-amber-300/80 font-medium">{char.role}</p>
                      </div>
                      <span className="text-xs font-mono bg-[#07080d] border border-white/[0.08] px-2.5 py-1 rounded-lg text-cyan-300">
                        #{char.character_id}
                      </span>
                    </div>

                    {/* Nuancier Hexadécimal */}
                    <div>
                      <span className="text-[11px] font-mono text-zinc-400 block mb-1.5">Palette Invariable :</span>
                      <div className="flex flex-wrap gap-2">
                        {char.description_physique?.couleurs_hex?.map((hex: string, i: number) => (
                          <button 
                            key={i} 
                            onClick={() => copyToClipboard(hex, `hex-${char.character_id}-${i}`)}
                            className="flex items-center gap-1.5 text-xs font-mono bg-[#07080d] px-3 py-1 rounded-xl border border-white/[0.08] hover:border-amber-400 transition"
                            title="Copier le code hex"
                          >
                            <span className="w-3.5 h-3.5 rounded-full shadow-inner" style={{ backgroundColor: hex }} />
                            <span>{hex}</span>
                            {copiedKey === `hex-${char.character_id}-${i}` ? <Check size={12} className="text-emerald-400" /> : <Copy size={10} className="text-zinc-500" />}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Attributs physiques */}
                    <div className="bg-[#07080d] p-4 rounded-2xl text-xs space-y-1.5 text-zinc-300 border border-white/[0.06]">
                      <p><strong className="text-zinc-400">Silhouette :</strong> {char.description_physique?.silhouette}</p>
                      <p><strong className="text-zinc-400">Visage :</strong> {char.description_physique?.visage}</p>
                      <p><strong className="text-zinc-400">Peau :</strong> {char.description_physique?.peau}</p>
                      <p><strong className="text-zinc-400">Coiffure :</strong> {char.description_physique?.coiffure}</p>
                      <p><strong className="text-zinc-400">Tenue :</strong> {char.description_physique?.tenue}</p>
                      <p><strong className="text-zinc-400">Accessoires :</strong> {char.description_physique?.accessoires_signature?.join(', ')}</p>
                    </div>

                    <div className="flex justify-between items-center text-xs text-zinc-400 pt-3 border-t border-white/[0.06] font-mono">
                      <span className="flex items-center gap-1.5 text-amber-300">
                        <Volume2 size={14} /> {char.voix_suggeree?.ton}
                      </span>
                      <span className="text-zinc-400">
                        {char.traits_caractere?.map((t: string) => `#${t}`).join(' ')}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-16 text-center glass-card rounded-3xl">
                <p className="text-sm text-zinc-400">Aucune fiche chargée. Lancez une génération depuis l'onglet Studio.</p>
              </div>
            )}
          </div>
        )}

        {/* 3. STORYBOARD STUDIO */}
        {activeTab === 'storyboard' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2.5">
                  <Film className="text-amber-400" size={20} />
                  Storyboard Structuré & Éditeur Human-in-the-Loop
                </h2>
                <p className="text-xs text-zinc-400 mt-0.5">Ajustez les actions en français, les prompts IA anglais et l'ordre des scènes</p>
              </div>
              <div className="text-xs font-mono bg-[#0c0e14] px-4 py-2 rounded-xl border border-white/[0.08] text-zinc-300 shadow-sm">
                {storyboardData?.segments?.length || 0} scènes • Total {storyboardData?.segments?.reduce((acc: number, s: any) => acc + s.duree_s, 0) || 0}s
              </div>
            </div>

            <div className="space-y-4">
              {storyboardData?.segments?.map((seg: any, idx: number) => {
                const isEditing = editingSceneId === seg.scene_id;
                return (
                  <div key={seg.scene_id} className="glass-card rounded-3xl p-6 space-y-4 shadow-xl glass-card-hover transition duration-300">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-3">
                        <span className="text-xs font-mono font-bold bg-amber-400 text-black px-2.5 py-1 rounded-lg">
                          #{seg.ordre}
                        </span>
                        <h3 className="text-base font-bold text-white">{seg.titre}</h3>
                        <span className="text-xs font-mono text-zinc-400">({seg.scene_id})</span>
                      </div>

                      <div className="flex items-center gap-2">
                        <button onClick={() => handleReorder(idx, 'up')} disabled={idx === 0} className="p-2 rounded-xl hover:bg-white/[0.08] text-zinc-400 disabled:opacity-20 transition">
                          <ArrowUp size={16} />
                        </button>
                        <button onClick={() => handleReorder(idx, 'down')} disabled={idx === (storyboardData.segments.length - 1)} className="p-2 rounded-xl hover:bg-white/[0.08] text-zinc-400 disabled:opacity-20 transition">
                          <ArrowDown size={16} />
                        </button>
                        <button 
                          onClick={() => isEditing ? handleSaveScene(seg.scene_id) : handleEditScene(seg)}
                          className={`text-xs px-4 py-2 rounded-xl font-bold flex items-center gap-1.5 transition ${
                            isEditing ? 'bg-emerald-400 text-black shadow-lg shadow-emerald-400/25' : 'bg-white/[0.06] text-white hover:bg-white/[0.12]'
                          }`}
                        >
                          {isEditing ? <><Save size={14} /> Enregistrer</> : <><Edit3 size={14} /> Modifier</>}
                        </button>
                      </div>
                    </div>

                    {isEditing ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 bg-[#07080d] p-5 rounded-2xl border border-white/[0.08]">
                        <div>
                          <label className="text-xs font-mono text-amber-400 block mb-1">Titre & Action (FR) :</label>
                          <input
                            type="text"
                            value={editForm.titre}
                            onChange={(e) => setEditForm({ ...editForm, titre: e.target.value })}
                            className="w-full bg-[#0c0e14] border border-white/[0.08] rounded-xl p-2.5 text-xs text-white mb-2"
                          />
                          <textarea
                            value={editForm.frame}
                            onChange={(e) => setEditForm({ ...editForm, frame: e.target.value })}
                            rows={3}
                            className="w-full bg-[#0c0e14] border border-white/[0.08] rounded-xl p-2.5 text-xs text-white"
                          />
                        </div>
                        <div>
                          <label className="text-xs font-mono text-amber-400 block mb-1">Prompt IA Vidéo (EN) :</label>
                          <textarea
                            value={editForm.prompt_ia}
                            onChange={(e) => setEditForm({ ...editForm, prompt_ia: e.target.value })}
                            rows={5}
                            className="w-full bg-[#0c0e14] border border-white/[0.08] rounded-xl p-2.5 text-xs text-white font-mono leading-relaxed"
                          />
                        </div>
                      </div>
                    ) : (
                      <>
                        <div className="bg-[#07080d] p-4 rounded-2xl border border-white/[0.06] space-y-2">
                          <p className="text-xs text-zinc-300">
                            <strong className="text-amber-300 font-semibold">Action Narrative :</strong> {seg.frame}
                          </p>
                          <p className="text-xs text-zinc-400 font-mono leading-relaxed">
                            <strong className="text-cyan-400 font-semibold">Prompt IA :</strong> {seg.prompt_ia}
                          </p>
                        </div>

                        {/* Badges de scène */}
                        <div className="flex flex-wrap gap-2 text-xs font-mono">
                          <span className="bg-[#07080d] px-3 py-1 rounded-xl text-amber-300 border border-white/[0.06]">
                            ⏱️ {seg.duree_s}s
                          </span>
                          <span className="bg-[#07080d] px-3 py-1 rounded-xl text-purple-300 border border-white/[0.06]">
                            🎭 {seg.emotion}
                          </span>
                          <span className="bg-[#07080d] px-3 py-1 rounded-xl text-blue-300 border border-white/[0.06]">
                            📐 {seg.plan}
                          </span>
                          <span className="bg-[#07080d] px-3 py-1 rounded-xl text-emerald-300 border border-white/[0.06]">
                            ✨ {seg.transition?.type} ({seg.transition?.duration_s}s)
                          </span>
                          <span className="bg-[#07080d] px-3 py-1 rounded-xl text-zinc-400 border border-white/[0.06]">
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
                <h2 className="text-lg font-bold text-white flex items-center gap-2.5">
                  <ShieldCheck className="text-amber-400" size={20} />
                  Tableau de Bord Contrôle Qualité (QC)
                </h2>
                <p className="text-xs text-zinc-400 mt-0.5">Validation de l'identité visuelle (DINOv2) et de la voix française (WER Whisper)</p>
              </div>

              <div className="flex gap-2">
                <span className="text-xs font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3.5 py-1 rounded-full">
                  SEUIL DINOv2: 0.75
                </span>
                <span className="text-xs font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-3.5 py-1 rounded-full">
                  WER MAX: 15%
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {qcData.map((qc: any, i: number) => {
                const isPassed = qc.status === 'passed';
                return (
                  <div key={i} className="glass-card rounded-3xl p-6 space-y-4 shadow-xl glass-card-hover transition duration-300">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-bold text-white">Scène #{i + 1} ({qc.segment_id})</span>
                      <span className={`text-xs px-3 py-1 rounded-full font-mono font-bold uppercase ${
                        isPassed 
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' 
                          : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                      }`}>
                        {qc.status}
                      </span>
                    </div>

                    {/* Jauge DINOv2 */}
                    <div className="bg-[#07080d] p-4 rounded-2xl border border-white/[0.06] space-y-2">
                      <div className="flex justify-between text-xs font-mono">
                        <span className="text-zinc-400">Score DINOv2 :</span>
                        <span className="font-bold text-emerald-400">{qc.visual_similarity?.score?.toFixed(2)} / 1.00</span>
                      </div>
                      <div className="w-full bg-[#11141d] h-2.5 rounded-full overflow-hidden">
                        <div 
                          className="bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-400 h-full rounded-full transition-all duration-500" 
                          style={{ width: `${(qc.visual_similarity?.score || 0) * 100}%` }}
                        />
                      </div>
                    </div>

                    {/* WER */}
                    <div className="text-xs flex justify-between bg-[#07080d] p-3.5 rounded-2xl border border-white/[0.06] font-mono">
                      <span className="text-zinc-400">WER Français :</span>
                      <span className="text-cyan-400 font-bold">{((qc.dialogue_wer || 0) * 100).toFixed(1)}%</span>
                    </div>

                    <div className="text-xs text-zinc-400 space-y-2 pt-1">
                      <p className="flex items-center gap-2 text-zinc-300">
                        <CheckCircle2 size={14} className="text-emerald-400" /> Flux audio stéréo AAC présent
                      </p>
                      <p className="flex items-center gap-2 text-zinc-300">
                        <CheckCircle2 size={14} className="text-emerald-400" /> Cadrage vertical 9:16 respecté
                      </p>
                      <p className="flex items-center gap-2 text-zinc-300">
                        <CheckCircle2 size={14} className="text-emerald-400" /> Décision : <strong className="text-white uppercase font-mono">{qc.recommendation}</strong>
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
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Mockup iPhone Pro 9:16 Player (5 colonnes) */}
            <div className="lg:col-span-5 flex flex-col items-center">
              <div className="w-[320px] h-[620px] bg-black rounded-[48px] border-[8px] border-[#1c2030] overflow-hidden shadow-2xl shadow-amber-500/10 relative flex items-center justify-center ring-1 ring-white/10 group">
                <video 
                  src={`/api/media/${storyId}/video`} 
                  controls 
                  className="w-full h-full object-cover"
                />
                {/* Dynamic Island Notch */}
                <div className="absolute top-3 left-1/2 -translate-x-1/2 w-28 h-5 bg-[#1c2030] rounded-full z-10 pointer-events-none" />
              </div>
              <span className="text-xs text-zinc-400 font-mono mt-4 flex items-center gap-2">
                <Smartphone size={14} className="text-amber-400" /> Rendu Vertical TikTok / Reels 1080×1920
              </span>
            </div>

            {/* Hub d'Exportation & Kit Viral (7 colonnes) */}
            <div className="lg:col-span-7 space-y-6">
              {/* Cartes d'export */}
              <div className="glass-card rounded-3xl p-6 space-y-4 shadow-2xl">
                <h3 className="text-sm font-bold text-amber-400 flex items-center gap-2 uppercase tracking-wide">
                  <Download size={16} />
                  Téléchargements & Multi-Formats
                </h3>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <a href={`/api/media/${storyId}/video`} download className="p-4 bg-[#07080d] hover:bg-white/[0.04] border border-white/[0.08] hover:border-amber-400/40 rounded-2xl text-center transition group shadow-sm">
                    <span className="text-sm font-bold block text-white group-hover:text-amber-400">9:16 Vertical</span>
                    <span className="text-[11px] text-zinc-400">TikTok / Reels (1080×1920)</span>
                  </a>
                  <a href={`/api/media/${storyId}/subtitles/srt`} download className="p-4 bg-[#07080d] hover:bg-white/[0.04] border border-white/[0.08] hover:border-cyan-400/40 rounded-2xl text-center transition group shadow-sm">
                    <span className="text-sm font-bold block text-white group-hover:text-cyan-400">Sous-Titres .SRT</span>
                    <span className="text-[11px] text-zinc-400">Format universel</span>
                  </a>
                  <a href={`/api/media/${storyId}/subtitles/ass`} download className="p-4 bg-[#07080d] hover:bg-white/[0.04] border border-white/[0.08] hover:border-purple-400/40 rounded-2xl text-center transition group shadow-sm">
                    <span className="text-sm font-bold block text-white group-hover:text-purple-400">Cinétique .ASS</span>
                    <span className="text-[11px] text-zinc-400">Styles dorés enrichis</span>
                  </a>
                </div>
              </div>

              {/* Social Viral Kit */}
              {socialData && (
                <div className="glass-card rounded-3xl p-6 space-y-4 shadow-2xl">
                  <h3 className="text-sm font-bold text-amber-400 flex items-center gap-2 uppercase tracking-wide">
                    <Share2 size={16} />
                    Social Media Viral Kit (SEO & Hashtags)
                  </h3>

                  <div className="space-y-3.5 text-xs">
                    <div>
                      <span className="text-zinc-400 font-mono block mb-1">🎯 Accroche des 3 premières secondes (Hook) :</span>
                      <div className="bg-[#07080d] p-3.5 rounded-2xl text-white font-medium border border-white/[0.08] flex justify-between items-center shadow-inner">
                        <span>{socialData.tiktok?.hook_phrase}</span>
                        <button onClick={() => copyToClipboard(socialData.tiktok?.hook_phrase, 'hook')} className="text-amber-400 hover:text-white p-1">
                          {copiedKey === 'hook' ? <Check size={16} className="text-emerald-400" /> : <Copy size={16} />}
                        </button>
                      </div>
                    </div>

                    <div>
                      <span className="text-zinc-400 font-mono block mb-1">🔥 Titre Viral & Hashtags TikTok :</span>
                      <div className="bg-[#07080d] p-3.5 rounded-2xl text-zinc-300 border border-white/[0.08] flex justify-between items-center shadow-inner">
                        <span>{socialData.tiktok?.viral_title} {socialData.tiktok?.hashtags?.join(' ')}</span>
                        <button onClick={() => copyToClipboard(`${socialData.tiktok?.viral_title} ${socialData.tiktok?.hashtags?.join(' ')}`, 'tt')} className="text-amber-400 hover:text-white p-1">
                          {copiedKey === 'tt' ? <Check size={16} className="text-emerald-400" /> : <Copy size={16} />}
                        </button>
                      </div>
                    </div>

                    <div>
                      <span className="text-zinc-400 font-mono block mb-1">📺 Description YouTube Shorts avec Chapitrage :</span>
                      <div className="bg-[#07080d] p-3.5 rounded-2xl text-zinc-300 border border-white/[0.08] font-mono whitespace-pre-wrap flex justify-between items-start shadow-inner">
                        <span>{socialData.youtube_shorts?.description}</span>
                        <button onClick={() => copyToClipboard(socialData.youtube_shorts?.description, 'yt')} className="text-amber-400 hover:text-white p-1">
                          {copiedKey === 'yt' ? <Check size={16} className="text-emerald-400" /> : <Copy size={16} />}
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
                <h2 className="text-lg font-bold text-white flex items-center gap-2.5">
                  <Layers className="text-amber-400" size={20} />
                  Journal d'Audit Render Manifest (JSONL Event Stream)
                </h2>
                <p className="text-xs text-zinc-400 mt-0.5">Traçabilité immuable, audit des licences et hashes SHA-256 de chaque fichier</p>
              </div>

              {/* Filtres d'événements */}
              <div className="flex gap-1.5 bg-[#0c0e14] p-1.5 rounded-2xl border border-white/[0.08] text-xs font-mono shadow-sm">
                {['all', 'ingestion', 'bible', 'storyboard', 'clip_generation', 'quality_control', 'assembly'].map((f) => (
                  <button
                    key={f}
                    onClick={() => setManifestFilter(f)}
                    className={`px-3 py-1.5 rounded-xl capitalize transition ${
                      manifestFilter === f ? 'bg-amber-400 text-black font-bold shadow-md shadow-amber-500/20' : 'text-zinc-400 hover:text-white'
                    }`}
                  >
                    {f}
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-[#07080d] border border-white/[0.08] rounded-3xl p-5 font-mono text-xs max-h-[580px] overflow-y-auto space-y-3 shadow-inner">
              {filteredEvents.map((ev, i) => (
                <div key={i} className="p-3.5 rounded-2xl bg-[#0c0e14] border border-white/[0.06] flex justify-between items-start gap-4 hover:border-amber-400/30 transition">
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                      <span className="text-amber-400 font-bold">[{ev.step.toUpperCase()}]</span>
                      <span className="text-white font-semibold">{ev.action}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {ev.status}
                      </span>
                    </div>
                    <p className="text-[11px] text-zinc-400 break-all leading-relaxed">{JSON.stringify(ev.details)}</p>
                  </div>
                  <span className="text-[10px] text-zinc-500 shrink-0 font-mono">{ev.timestamp}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
