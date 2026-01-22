import React from "react";
import {
  Shield,
  Brain,
  Eye,
  Zap,
  Database,
  Users,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";
import Button from "@/components/ui/Button";

export default function AboutPage() {
  const technologies = [
    {
      icon: <Brain className="h-8 w-8 text-primary-600" />,
      title: "Neural Networks",
      description:
        "Deep convolutional neural networks trained on millions of video frames to identify subtle manipulation patterns invisible to the human eye.",
    },
    {
      icon: <Eye className="h-8 w-8 text-primary-600" />,
      title: "Facial Analysis",
      description:
        "Advanced facial landmark detection and temporal consistency analysis to spot inconsistencies in facial movements and expressions.",
    },
    {
      icon: <Database className="h-8 w-8 text-primary-600" />,
      title: "Training Datasets",
      description:
        "Models trained on comprehensive datasets including FaceForensics++, DFDC, and CelebDF with diverse manipulation techniques.",
    },
    {
      icon: <Zap className="h-8 w-8 text-primary-600" />,
      title: "Real-time Processing",
      description:
        "Optimized inference pipeline with GPU acceleration for fast analysis while maintaining high accuracy and precision.",
    },
  ];

  const detectionMethods = [
    {
      title: "Frame-by-Frame Analysis",
      description:
        "Each video frame is analyzed individually using XceptionNet and ResNet architectures to detect pixel-level inconsistencies and artifacts.",
    },
    {
      title: "Temporal Consistency",
      description:
        "Sequential frame analysis detects unnatural temporal patterns and inconsistencies that occur in generated videos.",
    },
    {
      title: "Frequency Domain Analysis",
      description:
        "Examination of frequency components and spectral analysis to identify compression artifacts and generation signatures.",
    },
    {
      title: "Ensemble Methods",
      description:
        "Multiple detection models work together to provide robust and reliable deepfake identification with high confidence scores.",
    },
  ];

  const useCases = [
    {
      icon: <Shield className="h-6 w-6 text-primary-600" />,
      title: "Media Verification",
      description: "Verify authenticity of news videos and media content",
    },
    {
      icon: <Users className="h-6 w-6 text-primary-600" />,
      title: "Social Media",
      description: "Protect against misinformation and fake content",
    },
    {
      icon: <Eye className="h-6 w-6 text-primary-600" />,
      title: "Content Moderation",
      description: "Automated detection for platform content review",
    },
    {
      icon: <Shield className="h-6 w-6 text-primary-600" />,
      title: "Security & Forensics",
      description: "Digital forensics and evidence verification",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Hero Section */}
      <section className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-6">
              About Our Deepfake Detection System
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Advanced AI technology designed to identify manipulated videos and
              protect against digital deception. Learn how our system works and
              why it matters.
            </p>
          </div>
        </div>
      </section>

      {/* What is Deepfake Detection */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
                What is Deepfake Detection?
              </h2>
              <div className="space-y-4 text-gray-600 dark:text-gray-300">
                <p>
                  Deepfake detection is the process of identifying artificially
                  generated or manipulated video content using machine learning
                  and computer vision techniques. As deepfake technology becomes
                  more sophisticated, detection systems must evolve to stay
                  ahead.
                </p>
                <p>
                  Our system analyzes multiple aspects of video content
                  including facial inconsistencies, temporal artifacts,
                  compression patterns, and pixel-level anomalies to determine
                  the likelihood that a video has been artificially generated or
                  manipulated.
                </p>
                <p>
                  With the rise of accessible deepfake creation tools, reliable
                  detection has become crucial for maintaining trust in digital
                  media, preventing misinformation, and protecting individuals
                  from malicious use of their likeness.
                </p>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-8 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Key Statistics
              </h3>
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    Detection Accuracy
                  </span>
                  <span className="font-semibold text-primary-600">95.8%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    False Positive Rate
                  </span>
                  <span className="font-semibold text-green-600">&lt; 2%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    Processing Speed
                  </span>
                  <span className="font-semibold text-blue-600">
                    &lt; 2 min
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    Supported Formats
                  </span>
                  <span className="font-semibold text-gray-900 dark:text-white">
                    MP4, AVI, MOV
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Technologies Used */}
      <section className="py-16 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Technologies Behind Detection
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Our system combines cutting-edge AI techniques and proven computer
              vision methods to achieve industry-leading detection accuracy.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {technologies.map((tech, index) => (
              <div
                key={index}
                className="bg-gray-50 dark:bg-gray-900 p-8 rounded-xl"
              >
                <div className="mb-4">{tech.icon}</div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                  {tech.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {tech.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Detection Methods */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              How Detection Works
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Our multi-layered approach examines videos from multiple
              perspectives to identify even the most sophisticated deepfake
              manipulations.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {detectionMethods.map((method, index) => (
              <div
                key={index}
                className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm"
              >
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                  {method.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {method.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-16 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Real-World Applications
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Our deepfake detection technology serves various industries and
              use cases where content authenticity is critical.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {useCases.map((useCase, index) => (
              <div
                key={index}
                className="bg-gray-50 dark:bg-gray-900 p-6 rounded-xl text-center"
              >
                <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-100 dark:bg-primary-900/20 rounded-lg mb-4">
                  {useCase.icon}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  {useCase.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  {useCase.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Research & Models */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-primary-900 dark:bg-primary-950/20 border border-primary-200 dark:border-primary-800 rounded-xl p-8">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                Built on Scientific Research
              </h2>
              <p className="text-lg text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
                Our detection system is based on peer-reviewed research and
                state-of-the-art models including XceptionNet, EfficientNet, and
                custom architectures specifically designed for deepfake
                detection.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="text-center">
                  <div className="text-2xl font-bold text-white-600 mb-1">
                    XceptionNet
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Depthwise separable convolutions for feature extraction
                  </p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white-600 mb-1">
                    FaceForensics++
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Comprehensive training dataset with multiple manipulation
                    types
                  </p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white-600 mb-1">
                    Ensemble Learning
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Multiple models combined for robust detection
                  </p>
                </div>
              </div>

              <div className="text-center">
                <Link href="/detect">
                  <Button size="lg">
                    Try Detection System
                    <ArrowRight size={20} />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Limitations & Ethics */}
      <section className="py-16 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Limitations & Ethical Considerations
            </h2>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-amber-800 dark:text-amber-200 mb-4">
                Important Limitations
              </h3>
              <ul className="space-y-2 text-amber-700 dark:text-amber-300">
                <li>
                  • Detection accuracy may vary with video quality and
                  compression
                </li>
                <li>
                  • New deepfake techniques may temporarily evade detection
                </li>
                <li>
                  • Results should be part of comprehensive verification process
                </li>
                <li>
                  • False positives can occur with heavily processed legitimate
                  videos
                </li>
              </ul>
            </div>

            <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-blue-800 dark:text-blue-200 mb-4">
                Ethical Use Guidelines
              </h3>
              <ul className="space-y-2 text-blue-700 dark:text-blue-300">
                <li>
                  • Use detection results responsibly and with human oversight
                </li>
                <li>
                  • Consider privacy implications when analyzing personal
                  content
                </li>
                <li>
                  • Avoid using results for harassment or malicious purposes
                </li>
                <li>
                  • Report false positives/negatives to help improve the system
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
