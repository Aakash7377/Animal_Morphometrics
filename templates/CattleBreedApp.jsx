import React, { useState, useRef } from 'react';

/**
 * CattleBreedApp Component
 *
 * A clean, modern, AI-powered Cattle Breed Prediction UI built with React.js & Tailwind CSS.
 * Color Palette:
 * - Primary: #2E7D32 (Green)
 * - Secondary: #4CAF50 (Light Green)
 * - Background: #FFFFFF (Clean White)
 * - Light Gray Sections: #F5F7FA
 */

export default function CattleBreedApp() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/jpg'];
  const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png'];

  const validateAndSetFile = (selectedFile) => {
    setError(null);
    setResult(null);

    if (!selectedFile) return;

    const fileExt = '.' + selectedFile.name.split('.').pop().toLowerCase();
    const isValidType = ALLOWED_TYPES.includes(selectedFile.type) || ALLOWED_EXTENSIONS.includes(fileExt);

    if (!isValidType) {
      setError('Unable to process image. Please upload a valid JPG, JPEG, or PNG file.');
      setFile(null);
      setPreviewUrl(null);
      return;
    }

    setFile(selectedFile);
    const objectUrl = URL.createObjectURL(selectedFile);
    setPreviewUrl(objectUrl);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleClearImage = () => {
    setFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handlePredict = async () => {
    if (!file) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/predict', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to process image. Please try again.');
      }

      setResult({
        breed: data.breed,
        confidence: typeof data.confidence === 'number' ? data.confidence : parseFloat(data.confidence),
      });
    } catch (err) {
      setError(err.message || 'Unable to process image. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="min-h-screen bg-white text-gray-800 font-sans flex flex-col justify-between items-center px-4 py-8 md:py-14 selection:bg-[#2E7D32] selection:text-white">
      
      {/* Centered Main Layout */}
      <div className="w-full max-w-xl mx-auto flex flex-col gap-6">
        
        {/* 1. HEADER SECTION */}
        <header className="text-center flex flex-col items-center">
          <div className="flex items-center justify-center gap-3 mb-2">
            {/* Small Cattle Icon */}
            <div className="w-11 h-11 rounded-full bg-[#F5F7FA] border border-gray-200 flex items-center justify-center text-[#2E7D32] shadow-sm shrink-0">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-gray-900 tracking-tight">
              Cattle Breed Prediction
            </h1>
          </div>
          <p className="text-sm md:text-base text-gray-500 max-w-md">
            Upload a cattle image and let AI identify the breed instantly.
          </p>
        </header>

        {/* Centered Card Container */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-md p-6 sm:p-8 flex flex-col gap-6">
          
          {/* 2. UPLOAD CARD */}
          {!previewUrl ? (
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center min-h-[220px] ${
                isDragging
                  ? 'border-[#2E7D32] bg-[#2E7D32]/5 scale-[0.99]'
                  : 'border-gray-300 hover:border-[#2E7D32] bg-[#F5F7FA] hover:bg-gray-50'
              }`}
            >
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                accept=".jpg,.jpeg,.png"
                className="hidden"
              />
              
              {/* Upload Icon */}
              <div className="w-14 h-14 rounded-full bg-white shadow-sm border border-gray-200 flex items-center justify-center text-[#2E7D32] mb-3">
                <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              
              <p className="text-base font-semibold text-gray-800 mb-1">
                Drag &amp; Drop your cattle image here
              </p>
              <p className="text-sm text-[#2E7D32] font-medium mb-3">
                or click to browse
              </p>
              
              <div className="inline-flex items-center gap-1.5 text-xs text-gray-400 bg-white px-3 py-1 rounded-full border border-gray-200">
                <span>Supported formats:</span>
                <span className="font-semibold text-gray-600">JPG, JPEG, PNG</span>
              </div>
            </div>
          ) : (
            /* 3. IMAGE PREVIEW SECTION */
            <div className="flex flex-col gap-3">
              <div className="relative w-full aspect-[4/3] bg-gray-900 rounded-xl overflow-hidden shadow-inner flex items-center justify-center group">
                <img
                  src={previewUrl}
                  alt="Selected Cattle Preview"
                  className="w-full h-full object-cover rounded-xl transition-all duration-300"
                />
                <button
                  type="button"
                  onClick={handleClearImage}
                  className="absolute top-3 right-3 bg-black/60 hover:bg-black/80 text-white text-xs font-medium px-3 py-1.5 rounded-lg backdrop-blur-sm transition-all duration-150 flex items-center gap-1 shadow-sm"
                  title="Remove image"
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  Remove
                </button>
              </div>

              <div className="flex items-center justify-between px-1 text-xs text-gray-500">
                <span className="truncate max-w-[240px] font-medium text-gray-700" title={file?.name}>
                  {file?.name}
                </span>
                <span>{formatFileSize(file?.size)}</span>
              </div>
            </div>
          )}

          {/* 4. PREDICT BUTTON */}
          <button
            type="button"
            onClick={handlePredict}
            disabled={!file || isLoading}
            className={`w-full py-3.5 px-6 rounded-xl font-semibold text-base transition-all duration-200 flex items-center justify-center gap-2 shadow-sm ${
              !file || isLoading
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed shadow-none'
                : 'bg-[#2E7D32] hover:bg-[#256729] active:scale-[0.99] text-white shadow-md hover:shadow-lg'
            }`}
          >
            {isLoading ? (
              /* 5. LOADING STATE */
              <div className="flex items-center gap-2.5">
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Analyzing Image...</span>
              </div>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span>Predict Breed</span>
              </>
            )}
          </button>

          {/* 6. RESULT CARD */}
          {result && (
            <div className="bg-[#F5F7FA] border border-emerald-200/80 rounded-xl p-5 flex flex-col gap-4 animate-fadeIn transition-all duration-300">
              <div className="flex items-center justify-between border-b border-gray-200 pb-3">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#4CAF50] animate-pulse"></span>
                  <h3 className="font-semibold text-gray-900 text-sm tracking-wide uppercase">
                    Prediction Result
                  </h3>
                </div>
                
                {/* AI Badge */}
                <div className="inline-flex items-center gap-1.5 bg-[#2E7D32]/10 text-[#2E7D32] px-2.5 py-1 rounded-full text-xs font-semibold">
                  <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z" />
                  </svg>
                  <span>AI Verified</span>
                </div>
              </div>

              <div className="flex flex-col gap-3">
                <div className="flex items-baseline justify-between">
                  <span className="text-xs uppercase tracking-wider font-semibold text-gray-500">
                    Predicted Breed
                  </span>
                  <span className="text-xl font-bold text-[#2E7D32]">
                    {result.breed}
                  </span>
                </div>

                {/* Confidence Progress Bar */}
                <div className="flex flex-col gap-1.5">
                  <div className="flex items-center justify-between text-xs text-gray-600 font-medium">
                    <span>Confidence Score</span>
                    <span className="font-bold text-gray-900">{result.confidence.toFixed(2)}%</span>
                  </div>
                  
                  <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden p-0.5">
                    <div
                      className="h-full bg-gradient-to-r from-[#2E7D32] to-[#4CAF50] rounded-full transition-all duration-700 ease-out"
                      style={{ width: `${Math.min(Math.max(result.confidence, 5), 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 7. ERROR STATE */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 flex items-start gap-3 text-sm animate-fadeIn">
              <svg className="w-5 h-5 text-red-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <p className="font-semibold text-red-800">Unable to process image</p>
                <p className="text-red-600 text-xs mt-0.5">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* 8. FOOTER */}
        <footer className="text-center pt-2">
          <p className="text-xs text-gray-400 font-medium">
            Powered by AI Breed Classification Model
          </p>
        </footer>

      </div>
    </div>
  );
}
