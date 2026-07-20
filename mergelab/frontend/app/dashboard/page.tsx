"use client";

import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { motion } from "framer-motion";
import { Activity, History, HardDrive, Trash2, Share2, Download } from "lucide-react";

interface MergeHistoryItem {
  id: string;
  name: string;
  model_a: string;
  model_b: string;
  method: string;
  date: string;
  status: string;
  size: string;
}

export default function DashboardPage() {
  const [mergeHistory, setMergeHistory] = useState<MergeHistoryItem[]>([]);
  const [storageUsed, setStorageUsed] = useState(0);
  const [totalMerges, setTotalMerges] = useState(0);

  // Mock data for demonstration
  useEffect(() => {
    // In production, fetch from API
    setMergeHistory([
      {
        id: "abc123",
        name: "Qwen-Llama-Mix",
        model_a: "Qwen/Qwen2.5-7B-Instruct",
        model_b: "meta-llama/Llama-3.1-8B-Instruct",
        method: "slerp",
        date: "2026-01-15",
        status: "completed",
        size: "4.2 GB"
      },
      {
        id: "def456",
        name: "Mistral-Phi-Blend",
        model_a: "mistralai/Mistral-7B-Instruct-v0.3",
        model_b: "microsoft/Phi-3-mini-4k-instruct",
        method: "ties",
        date: "2026-01-14",
        status: "completed",
        size: "3.8 GB"
      },
      {
        id: "ghi789",
        name: "Gemma-Yi-Fusion",
        model_a: "google/gemma-2-9b-it",
        model_b: "01-ai/Yi-1.5-9B-Chat",
        method: "dare",
        date: "2026-01-13",
        status: "completed",
        size: "5.1 GB"
      }
    ]);
    
    setStorageUsed(13.1);
    setTotalMerges(3);
  }, []);

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
            <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
            <p className="text-gray-400">
              Manage your merges, storage, and API keys
            </p>
          </motion.div>

          {/* Stats */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="glass p-6 rounded-xl"
            >
              <div className="flex items-center space-x-3 mb-3">
                <Activity className="w-6 h-6 text-accent" />
                <span className="text-gray-400">Total Merges</span>
              </div>
              <p className="text-3xl font-bold">{totalMerges}</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass p-6 rounded-xl"
            >
              <div className="flex items-center space-x-3 mb-3">
                <HardDrive className="w-6 h-6 text-accent" />
                <span className="text-gray-400">Storage Used</span>
              </div>
              <p className="text-3xl font-bold">{storageUsed.toFixed(1)} GB</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="glass p-6 rounded-xl"
            >
              <div className="flex items-center space-x-3 mb-3">
                <Share2 className="w-6 h-6 text-accent" />
                <span className="text-gray-400">Active Deployments</span>
              </div>
              <p className="text-3xl font-bold">0</p>
            </motion.div>
          </div>

          {/* Merge History */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="glass rounded-xl overflow-hidden"
          >
            <div className="p-6 border-b border-white/10">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <History className="w-6 h-6 text-accent" />
                  <h2 className="text-xl font-semibold">Merge History</h2>
                </div>
              </div>
            </div>

            {mergeHistory.length === 0 ? (
              <div className="p-12 text-center text-gray-400">
                <History className="w-12 h-12 mx-auto mb-4 opacity-30" />
                <p>No merges yet</p>
                <a href="/merge" className="text-accent hover:text-accent/80 mt-2 inline-block">
                  Create your first merge →
                </a>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-white/5">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Models
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Method
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Size
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/10">
                    {mergeHistory.map((merge) => (
                      <tr key={merge.id} className="hover:bg-white/5 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="font-medium">{merge.name}</span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-400">
                            <p className="truncate max-w-[200px]">{merge.model_a}</p>
                            <p className="truncate max-w-[200px] text-xs">+ {merge.model_b}</p>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 py-1 bg-accent/20 text-accent rounded text-xs uppercase">
                            {merge.method}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                          {merge.date}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                          {merge.size}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 py-1 bg-green-500/20 text-green-500 rounded text-xs">
                            {merge.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          <div className="flex items-center justify-end space-x-2">
                            <button className="p-2 hover:bg-white/10 rounded transition-colors" title="Download">
                              <Download className="w-4 h-4" />
                            </button>
                            <button className="p-2 hover:bg-white/10 rounded transition-colors" title="Share">
                              <Share2 className="w-4 h-4" />
                            </button>
                            <button className="p-2 hover:bg-red-500/20 rounded transition-colors text-red-500" title="Delete">
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </motion.div>

          {/* API Keys Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="glass rounded-xl p-6 mt-8"
          >
            <h2 className="text-xl font-semibold mb-4">API Keys</h2>
            <p className="text-gray-400 mb-4">
              Manage your API keys for deployed models
            </p>
            <button className="gradient-btn px-6 py-3 rounded-lg font-medium">
              Generate New API Key
            </button>
          </motion.div>
        </div>
      </main>

      <Footer />
    </>
  );
}
