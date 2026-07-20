"use client";

import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { modelsApi } from "@/lib/api";
import { Model } from "@/lib/types";
import { motion } from "framer-motion";
import { Search, Filter, Download, Cpu, HardDrive, FileText } from "lucide-react";

export default function ModelsPage() {
  const [models, setModels] = useState<Model[]>([]);
  const [filteredModels, setFilteredModels] = useState<Model[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [selectedFamily, setSelectedFamily] = useState<string>("all");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadModels = async () => {
      try {
        const response = await modelsApi.list();
        setModels(response.data.models);
        setFilteredModels(response.data.models);
      } catch (error) {
        console.error("Error loading models:", error);
      } finally {
        setIsLoading(false);
      }
    };
    loadModels();
  }, []);

  useEffect(() => {
    let filtered = models;

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (m) =>
          m.id.toLowerCase().includes(query) ||
          m.name.toLowerCase().includes(query)
      );
    }

    if (selectedCategory !== "all") {
      filtered = filtered.filter((m) => m.category === selectedCategory);
    }

    if (selectedFamily !== "all") {
      filtered = filtered.filter((m) => m.family.toLowerCase() === selectedFamily.toLowerCase());
    }

    setFilteredModels(filtered);
  }, [searchQuery, selectedCategory, selectedFamily, models]);

  const families = [...new Set(models.map((m) => m.family))];

  return (
    <>
      <Navbar />

      <main className="flex-1 py-8 px-4">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h1 className="text-3xl font-bold mb-2">Available Models</h1>
            <p className="text-gray-400">
              Browse and select from {models.length} popular AI models for merging
            </p>
          </motion.div>

          {/* Filters */}
          <div className="glass p-4 rounded-xl mb-8">
            <div className="grid md:grid-cols-4 gap-4">
              {/* Search */}
              <div className="md:col-span-2 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search models..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-card border border-white/10 rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:border-accent transition-colors"
                />
              </div>

              {/* Category Filter */}
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="bg-card border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:border-accent transition-colors"
              >
                <option value="all">All Categories</option>
                <option value="slm">SLM (1-3B)</option>
                <option value="medium">Medium (7-8B)</option>
                <option value="large">Large (70B+)</option>
              </select>

              {/* Family Filter */}
              <select
                value={selectedFamily}
                onChange={(e) => setSelectedFamily(e.target.value)}
                className="bg-card border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:border-accent transition-colors"
              >
                <option value="all">All Families</option>
                {families.map((family) => (
                  <option key={family} value={family}>
                    {family}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Results Count */}
          <div className="mb-6 flex items-center justify-between">
            <p className="text-gray-400">
              Showing {filteredModels.length} of {models.length} models
            </p>
          </div>

          {/* Models Grid */}
          {isLoading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="glass p-6 rounded-xl animate-pulse">
                  <div className="h-6 bg-white/10 rounded mb-4" />
                  <div className="h-4 bg-white/10 rounded w-2/3 mb-2" />
                  <div className="h-4 bg-white/10 rounded w-1/2" />
                </div>
              ))}
            </div>
          ) : filteredModels.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <Filter className="w-12 h-12 mx-auto mb-4 opacity-30" />
              <p>No models found matching your criteria</p>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredModels.map((model, i) => (
                <motion.div
                  key={model.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="glass p-6 rounded-xl hover:border-accent/50 transition-all cursor-pointer group"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="font-semibold group-hover:text-accent transition-colors">
                        {model.name}
                      </h3>
                      <p className="text-xs text-gray-500 mono">{model.id}</p>
                    </div>
                    <span
                      className={`px-2 py-1 rounded text-xs ${
                        model.category === "slm"
                          ? "bg-green-500/20 text-green-500"
                          : model.category === "medium"
                          ? "bg-yellow-500/20 text-yellow-500"
                          : "bg-red-500/20 text-red-500"
                      }`}
                    >
                      {model.parameters}
                    </span>
                  </div>

                  <div className="space-y-2 text-sm text-gray-400">
                    <div className="flex items-center space-x-2">
                      <Cpu className="w-4 h-4" />
                      <span>{model.family} Family</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <HardDrive className="w-4 h-4" />
                      <span>{model.size_gb.toFixed(1)} GB</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <FileText className="w-4 h-4" />
                      <span>{model.license}</span>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-white/10 flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      {(model.downloads / 1000).toFixed(0)}k downloads
                    </span>
                    <a
                      href={`/merge?model_a=${encodeURIComponent(model.id)}`}
                      className="text-sm text-accent hover:text-accent/80 transition-colors"
                    >
                      Use this →
                    </a>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </main>

      <Footer />
    </>
  );
}
