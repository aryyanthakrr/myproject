"use client";

import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import MergeConfig from "@/components/MergeConfig";
import ProgressBar from "@/components/ProgressBar";
import { modelsApi, mergeApi } from "@/lib/api";
import { Model } from "@/lib/types";
import { motion } from "framer-motion";
import { FlaskConical, ArrowRightLeft } from "lucide-react";

export default function MergePage() {
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModelA, setSelectedModelA] = useState("");
  const [selectedModelB, setSelectedModelB] = useState("");
  const [selectedMethod, setSelectedMethod] = useState("slerp");
  const [ratio, setRatio] = useState(0.5);
  const [outputFormat, setOutputFormat] = useState("gguf-4bit");
  const [outputName, setOutputName] = useState("");
  const [isMerging, setIsMerging] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    const loadModels = async () => {
      try {
        const response = await modelsApi.list();
        setModels(response.data.models);
      } catch (error) {
        console.error("Error loading models:", error);
      }
    };
    loadModels();
  }, []);

  const handleMerge = async () => {
    if (!selectedModelA || !selectedModelB || !outputName) return;

    setIsMerging(true);
    try {
      const response = await mergeApi.create({
        model_a: selectedModelA,
        model_b: selectedModelB,
        method: selectedMethod,
        ratio,
        output_format: outputFormat,
        output_name: outputName,
      });
      setJobId(response.data.job_id);
    } catch (error) {
      console.error("Error creating merge job:", error);
      setIsMerging(false);
    }
  };

  const handleComplete = (mergeResult: any) => {
    setResult(mergeResult);
    setIsMerging(false);
  };

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
            <div className="flex items-center space-x-3 mb-2">
              <FlaskConical className="w-8 h-8 text-accent" />
              <h1 className="text-3xl font-bold">Merge Models</h1>
            </div>
            <p className="text-gray-400">
              Select two models, choose a merge method, and create your custom AI
            </p>
          </motion.div>

          {/* Main Content */}
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Left Panel - Configuration */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="glass p-6 rounded-2xl"
            >
              <h2 className="text-xl font-semibold mb-6 flex items-center space-x-2">
                <ArrowRightLeft className="w-5 h-5 text-accent" />
                <span>Configuration</span>
              </h2>

              <MergeConfig
                models={models}
                selectedModelA={selectedModelA}
                selectedModelB={selectedModelB}
                selectedMethod={selectedMethod}
                ratio={ratio}
                outputFormat={outputFormat}
                outputName={outputName}
                onModelAChange={setSelectedModelA}
                onModelBChange={setSelectedModelB}
                onMethodChange={setSelectedMethod}
                onRatioChange={setRatio}
                onOutputFormatChange={setOutputFormat}
                onOutputNameChange={setOutputName}
                onMerge={handleMerge}
                isMerging={isMerging}
              />
            </motion.div>

            {/* Right Panel - Progress & Results */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="glass p-6 rounded-2xl"
            >
              <h2 className="text-xl font-semibold mb-6">Progress</h2>
              
              {!jobId && !result ? (
                <div className="text-center py-12 text-gray-400">
                  <FlaskConical className="w-16 h-16 mx-auto mb-4 opacity-30" />
                  <p>Your merge progress will appear here</p>
                  <p className="text-sm mt-2">Configure your merge and click MERGE to start</p>
                </div>
              ) : (
                <ProgressBar jobId={jobId} onComplete={handleComplete} />
              )}

              {/* Result Info */}
              {result?.status === 'completed' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-6 p-4 bg-green-500/10 border border-green-500 rounded-lg"
                >
                  <h3 className="font-semibold text-green-500 mb-2">✅ Merge Complete!</h3>
                  <div className="space-y-1 text-sm">
                    <p><span className="text-gray-400">Name:</span> {result.output_name}</p>
                    <p><span className="text-gray-400">Format:</span> {result.format}</p>
                    <p><span className="text-gray-400">Size:</span> {result.file_size_human}</p>
                    <p className="mono text-xs text-gray-500 break-all">
                      <span className="text-gray-400">SHA-256:</span> {result.sha256_hash}
                    </p>
                  </div>
                </motion.div>
              )}
            </motion.div>
          </div>
        </div>
      </main>

      <Footer />
    </>
  );
}
