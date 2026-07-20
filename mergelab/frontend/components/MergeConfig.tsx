"use client";

import { motion } from "framer-motion";
import { FlaskConical, Download, MessageSquare, Cloud, Share2, Key } from "lucide-react";
import { useState } from "react";
import { mergeApi, TestResponse } from "@/lib/api";
import { MERGE_METHODS, OUTPUT_FORMATS } from "@/lib/types";

interface MergeConfigProps {
  models: any[];
  selectedModelA: string;
  selectedModelB: string;
  selectedMethod: string;
  ratio: number;
  outputFormat: string;
  outputName: string;
  onModelAChange: (value: string) => void;
  onModelBChange: (value: string) => void;
  onMethodChange: (value: string) => void;
  onRatioChange: (value: number) => void;
  onOutputFormatChange: (value: string) => void;
  onOutputNameChange: (value: string) => void;
  onMerge: () => void;
  isMerging: boolean;
}

export default function MergeConfig({
  models,
  selectedModelA,
  selectedModelB,
  selectedMethod,
  ratio,
  outputFormat,
  outputName,
  onModelAChange,
  onModelBChange,
  onMethodChange,
  onRatioChange,
  onOutputFormatChange,
  onOutputNameChange,
  onMerge,
  isMerging,
}: MergeConfigProps) {
  return (
    <div className="space-y-6">
      {/* Model Selection */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Model A
          </label>
          <select
            value={selectedModelA}
            onChange={(e) => onModelAChange(e.target.value)}
            className="w-full bg-card border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-accent transition-colors"
          >
            <option value="">Select Model A</option>
            {models.map((model) => (
              <option key={model.id} value={model.id}>
                {model.name} ({model.parameters})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Model B
          </label>
          <select
            value={selectedModelB}
            onChange={(e) => onModelBChange(e.target.value)}
            className="w-full bg-card border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-accent transition-colors"
          >
            <option value="">Select Model B</option>
            {models.map((model) => (
              <option key={model.id} value={model.id}>
                {model.name} ({model.parameters})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Merge Method */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-3">
          Merge Method
        </label>
        <div className="space-y-2">
          {MERGE_METHODS.map((method) => (
            <label
              key={method.id}
              className={`flex items-start p-3 rounded-lg border cursor-pointer transition-all ${
                selectedMethod === method.id
                  ? 'border-accent bg-accent/10'
                  : 'border-white/10 hover:border-white/20'
              }`}
            >
              <input
                type="radio"
                name="method"
                value={method.id}
                checked={selectedMethod === method.id}
                onChange={(e) => onMethodChange(e.target.value)}
                className="mt-1 w-4 h-4 text-accent focus:ring-accent"
              />
              <div className="ml-3">
                <div className="flex items-center space-x-2">
                  <span className="font-medium">{method.name}</span>
                  {method.recommended && (
                    <span className="text-xs bg-accent/20 text-accent px-2 py-0.5 rounded">
                      Recommended
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-400">{method.description}</p>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Mix Ratio */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Mix Ratio: {Math.round(ratio * 100)}% Model B / {Math.round((1 - ratio) * 100)}% Model A
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={ratio}
          onChange={(e) => onRatioChange(parseFloat(e.target.value))}
          className="w-full h-2 bg-card rounded-lg appearance-none cursor-pointer accent-accent"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>100% A</span>
          <span>50/50</span>
          <span>100% B</span>
        </div>
      </div>

      {/* Output Format */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Output Format
        </label>
        <select
          value={outputFormat}
          onChange={(e) => onOutputFormatChange(e.target.value)}
          className="w-full bg-card border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-accent transition-colors"
        >
          {OUTPUT_FORMATS.map((format) => (
            <option key={format.id} value={format.id}>
              {format.name}
            </option>
          ))}
        </select>
      </div>

      {/* Output Name */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Output Name
        </label>
        <input
          type="text"
          value={outputName}
          onChange={(e) => onOutputNameChange(e.target.value)}
          placeholder="MyMergedModel"
          className="w-full bg-card border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-accent transition-colors"
        />
      </div>

      {/* Merge Button */}
      <button
        onClick={onMerge}
        disabled={isMerging || !selectedModelA || !selectedModelB || !outputName}
        className="w-full gradient-btn py-4 rounded-xl font-semibold text-lg flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <FlaskConical className="w-5 h-5" />
        <span>{isMerging ? 'Merging...' : '🚀 MERGE'}</span>
      </button>
    </div>
  );
}
