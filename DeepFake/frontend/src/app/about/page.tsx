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
      title: "Facial Embeddings",
      description:
        "FaceNet and MobileNetV2 models generate 128-dimensional identity embeddings for precise matching against protected creator databases.",
    },
    {
      icon: <Eye className="h-8 w-8 text-primary-600" />,
      title: "Identity Matching",
      description:
        "Cosine similarity algorithms compare facial embeddings with 96%+ accuracy to identify unauthorized use of protected identities.",
    },
    {
      icon: <Database className="h-8 w-8 text-primary-600" />,
      title: "Protected Entity Registry",
      description:
        "Secure database storing creator identity embeddings, licensing information, and violation logs for comprehensive rights management.",
    },
    {
      icon: <Zap className="h-8 w-8 text-primary-600" />,
      title: "Dual-Layer Detection",
      description:
        "XceptionNet authenticates content first, then identity matching runs on AI-generated media for copyright enforcement.",
    },
  ];

  const detectionMethods = [
    {
      title: "Authenticity Verification",
      description:
        "XceptionNet and ResNet architectures analyze video frames to determine if content is AI-generated or authentic before copyright checks.",
    },
    {
      title: "Face Detection & Extraction",
      description:
        "Dlib HOG and OpenCV DNN models detect faces in flagged frames, extracting facial regions for embedding generation.",
    },
    {
      title: "Embedding Comparison",
      description:
        "128-dimensional facial vectors are compared against protected creator embeddings using cosine similarity with 0.60 threshold.",
    },
    {
      title: "Licensing Enforcement",
      description:
        "Matched identities trigger license validation, logging violations and providing detailed reports on unauthorized usage.",
    },
  ];

  const useCases = [
    {
      icon: <Shield className="h-6 w-6 text-primary-600" />,
      title: "Creator Protection",
      description:
        "Safeguard identities from unauthorized AI-generated content",
    },
    {
      icon: <Users className="h-6 w-6 text-primary-600" />,
      title: "Rights Management",
      description: "Enforce licensing agreements and track usage violations",
    },
    {
      icon: <Eye className="h-6 w-6 text-primary-600" />,
      title: "Content Verification",
      description: "Verify authenticity and provenance of digital media",
    },
    {
      icon: <Shield className="h-6 w-6 text-primary-600" />,
      title: "Brand Protection",
      description: "Detect unauthorized use of celebrity and brand identities",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Hero Section */}
      <section className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-6">
              About Copyright Detection in Generative AI
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Advanced AI technology designed to protect creator identities from
              unauthorized use in AI-generated content. Learn how our dual-layer
              system works and why it matters for creator rights.
            </p>
          </div>
        </div>
      </section>

      {/* What is Copyright Detection */}
      <section className="py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-6">
              What is Copyright Detection in Generative AI?
            </h2>
          </div>

          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 p-8 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-primary-100 dark:bg-primary-900/20 rounded-lg flex items-center justify-center">
                  <Shield className="w-6 h-6 text-primary-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                    Protecting Creator Identities
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                    Copyright detection in generative AI identifies when
                    protected creator identities are used without authorization
                    in AI-generated content. Our system combines authenticity
                    verification with identity matching to protect creator
                    rights.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-8 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                  <Zap className="w-6 h-6 text-blue-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                    Dual-Layer Detection Workflow
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                    The workflow starts by verifying if content is AI-generated
                    using deepfake detection. For synthetic content, we extract
                    facial embeddings and match them against our database of
                    protected identities, checking for licensing violations and
                    unauthorized usage.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-8 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                  <Users className="w-6 h-6 text-green-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                    Empowering Creators
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                    With the widespread availability of generative AI tools,
                    protecting creator identities has become critical. Our
                    system empowers creators to register their likeness, enforce
                    licensing agreements, and detect violations across digital
                    platforms.
                  </p>
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
              Technologies Behind Copyright Detection
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Our system combines facial recognition, embedding matching, and
              authenticity verification to achieve comprehensive creator
              protection.
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
              How Copyright Detection Works
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Our dual-layer approach first verifies authenticity, then matches
              identities\n against protected creator databases to detect
              violations.\n{" "}
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
              Our copyright detection technology protects creators across
              entertainment,\n media, and digital platforms where identity
              rights are critical.\n{" "}
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
                Built on Advanced AI Technology
              </h2>
              <p className="text-lg text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
                Our copyright detection system combines facial recognition
                models, embedding matching algorithms, and deepfake detection
                architectures to provide comprehensive creator protection.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="text-center">
                  <div className="text-2xl font-bold text-white-600 mb-1">
                    FaceNet/MobileNetV2
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    128-dimensional facial embeddings for identity matching
                  </p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white-600 mb-1">
                    XceptionNet
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Deep CNN for authenticity verification and deepfake
                    detection
                  </p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white-600 mb-1">
                    Cosine Similarity
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    High-accuracy identity matching with 0.60 threshold
                  </p>
                </div>
              </div>

              <div className="text-center">
                <Link href="/detect">
                  <Button size="lg">
                    Analyze Content
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
              System Limitations & Privacy
            </h2>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-amber-800 dark:text-amber-200 mb-4">
                System Limitations
              </h3>
              <ul className="space-y-2 text-amber-700 dark:text-amber-300">
                <li>
                  • Identity matching accuracy depends on reference photo
                  quality
                </li>
                <li>
                  • New generative AI techniques may temporarily evade detection
                </li>
                <li>
                  • Cosine similarity threshold may produce false matches in
                  edge cases
                </li>
                <li>
                  • Results should be combined with human review for enforcement
                </li>
              </ul>
            </div>

            <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-blue-800 dark:text-blue-200 mb-4">
                Privacy & Ethics
              </h3>
              <ul className="space-y-2 text-blue-700 dark:text-blue-300">
                <li>
                  • Creator embeddings are stored securely and used only for
                  protection
                </li>
                <li>
                  • Uploaded content is analyzed and not permanently stored
                </li>
                <li>
                  • Creators can delete their protected identity at any time
                </li>
                <li>
                  • System designed to empower creators, not surveil or censor
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
