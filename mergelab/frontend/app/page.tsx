"use client";

import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { motion } from "framer-motion";
import { FlaskConical, Zap, Download, Cloud, Shield, Sparkles } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <>
      <Navbar />
      
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative py-20 px-4 overflow-hidden">
          {/* Background gradient */}
          <div className="absolute inset-0 bg-gradient-to-b from-accent/10 to-transparent pointer-events-none" />
          
          <div className="max-w-7xl mx-auto text-center relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-accent/20 text-accent mb-6">
                <Sparkles className="w-4 h-4 mr-2" />
                Powered by intellectlabs
              </span>
              
              <h1 className="text-5xl md:text-7xl font-bold mb-6">
                Merge AI Models in{" "}
                <span className="gradient-text">One Click</span>
              </h1>
              
              <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
                Select two models. Choose a method. Click merge. 
                Download your custom AI ready for deployment.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  href="/merge"
                  className="gradient-btn px-8 py-4 rounded-xl font-semibold text-lg flex items-center justify-center space-x-2"
                >
                  <FlaskConical className="w-5 h-5" />
                  <span>Start Merging →</span>
                </Link>
                
                <Link
                  href="/models"
                  className="px-8 py-4 rounded-xl font-semibold text-lg border border-white/20 hover:border-white/40 transition-colors"
                >
                  Browse Models
                </Link>
              </div>
            </motion.div>
            
            {/* Stats */}
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-16"
            >
              {[
                { value: "50+", label: "Models Available" },
                { value: "5", label: "Merge Methods" },
                { value: "GGUF", label: "Export Format" },
                { value: "Free", label: "To Start" },
              ].map((stat, i) => (
                <div key={i} className="text-center">
                  <div className="text-3xl md:text-4xl font-bold gradient-text">{stat.value}</div>
                  <div className="text-gray-400 text-sm mt-1">{stat.label}</div>
                </div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* How It Works */}
        <section className="py-20 px-4 bg-card/50">
          <div className="max-w-7xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
            
            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  icon: <FlaskConical className="w-8 h-8" />,
                  title: "1. Select Models",
                  description: "Choose two AI models from our library of 50+ popular models including Qwen, Llama, Mistral, and more."
                },
                {
                  icon: <Zap className="w-8 h-8" />,
                  title: "2. Choose Method",
                  description: "Pick a merge method: SLERP for smooth blending, TIES for smart merging, DARE for advanced combinations, or Linear for simplicity."
                },
                {
                  icon: <Download className="w-8 h-8" />,
                  title: "3. Download & Deploy",
                  description: "Get your merged model in GGUF format with SHA-256 verification. Download, test, or deploy instantly."
                }
              ].map((step, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: i * 0.1 }}
                  viewport={{ once: true }}
                  className="glass p-8 rounded-2xl text-center hover:border-accent/50 transition-colors"
                >
                  <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-primary flex items-center justify-center text-white">
                    {step.icon}
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{step.title}</h3>
                  <p className="text-gray-400">{step.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Popular Merges */}
        <section className="py-20 px-4">
          <div className="max-w-7xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12">Popular Merges</h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { name: "Qwen + Llama", models: "Qwen2.5-7B + Llama-3.1-8B", desc: "Reasoning + Instruction Following" },
                { name: "Mistral + Phi", models: "Mistral-7B + Phi-3-mini", desc: "Efficiency + Compact Knowledge" },
                { name: "Gemma + Yi", models: "Gemma-2-9B + Yi-1.5-9B", desc: "Google + Alibaba Capabilities" },
                { name: "SLM Power", models: "Qwen2.5-3B + Phi-3-mini", desc: "Powerful Small Language Model" }
              ].map((merge, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.4, delay: i * 0.1 }}
                  viewport={{ once: true }}
                  className="glass p-6 rounded-xl hover:border-accent/50 transition-all cursor-pointer group"
                >
                  <div className="flex items-center space-x-2 mb-3">
                    <Cloud className="w-5 h-5 text-accent" />
                    <h3 className="font-semibold group-hover:text-accent transition-colors">{merge.name}</h3>
                  </div>
                  <p className="text-sm text-gray-400 mb-2">{merge.models}</p>
                  <p className="text-xs text-gray-500">{merge.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="py-20 px-4 bg-card/50">
          <div className="max-w-7xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12">Why MergeLab?</h2>
            
            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  icon: <Shield className="w-6 h-6" />,
                  title: "SHA-256 Verification",
                  description: "Every download includes integrity certificates to ensure your models are authentic and unmodified."
                },
                {
                  icon: <Cloud className="w-6 h-6" />,
                  title: "HuggingFace Integration",
                  description: "Push your merged models directly to HuggingFace Hub with auto-generated model cards."
                },
                {
                  icon: <Zap className="w-6 h-6" />,
                  title: "GGUF Export",
                  description: "Quantize to 2-bit, 4-bit, 5-bit, 8-bit, or F16 for optimal performance on any hardware."
                }
              ].map((feature, i) => (
                <div key={i} className="flex space-x-4">
                  <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-accent/20 flex items-center justify-center text-accent">
                    {feature.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold mb-2">{feature.title}</h3>
                    <p className="text-gray-400 text-sm">{feature.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-20 px-4">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-4xl font-bold mb-6">Ready to Create Your Custom AI?</h2>
            <p className="text-gray-400 mb-8">
              Join thousands of developers and researchers using MergeLab to create powerful merged models.
            </p>
            <Link
              href="/merge"
              className="gradient-btn inline-block px-10 py-4 rounded-xl font-semibold text-lg"
            >
              Start Merging Now →
            </Link>
          </div>
        </section>
      </main>

      <Footer />
    </>
  );
}
