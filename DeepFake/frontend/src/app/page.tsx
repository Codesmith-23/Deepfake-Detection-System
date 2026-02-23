"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Shield,
  Eye,
  Zap,
  Users,
  ArrowRight,
  LogIn,
  UserPlus,
} from "lucide-react";
import Button from "@/components/ui/Button";
import { authService } from "@/lib/auth";

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    setIsAuthenticated(authService.isAuthenticated());
  }, []);

  const features = [
    {
      icon: <Shield className="h-8 w-8 text-primary-600" />,
      title: "Identity Protection",
      description:
        "Safeguard creator identities from unauthorized use in AI-generated content with facial recognition and embedding matching.",
    },
    {
      icon: <Eye className="h-8 w-8 text-primary-600" />,
      title: "Copyright Enforcement",
      description:
        "Automatically detect and flag violations of protected identities, supporting licensing and rights management.",
    },
    {
      icon: <Zap className="h-8 w-8 text-primary-600" />,
      title: "Dual-Layer Detection",
      description:
        "Combines authenticity verification with provenance tracking to identify both deepfakes and copyright infringement.",
    },
    {
      icon: <Users className="h-8 w-8 text-primary-600" />,
      title: "Creator Registration",
      description:
        "Simple interface for creators to register their identity, upload reference photos, and protect their likeness.",
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-primary-50 to-primary-100 dark:from-gray-900 dark:to-gray-800 py-20 sm:py-32">
        <div className="absolute inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] dark:bg-grid-slate-700/25" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold text-gray-900 dark:text-white mb-8">
              Copyright Detection in
              <br />
              <span className="text-primary-600">Generative AI</span>
            </h1>

            <p className="text-xl sm:text-2xl text-gray-600 dark:text-gray-300 mb-12 max-w-3xl mx-auto">
              Protect creator rights and verify content authenticity with our
              AI-powered system that detects copyright violations in
              AI-generated media.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {isAuthenticated ? (
                <>
                  <Link href="/detect">
                    <Button
                      size="lg"
                      className="w-full sm:w-auto text-lg px-8 py-4"
                    >
                      Get Started
                      <ArrowRight size={20} />
                    </Button>
                  </Link>
                  <Link href="/about">
                    <Button
                      variant="outline"
                      size="lg"
                      className="w-full sm:w-auto text-lg px-8 py-4"
                    >
                      Learn More
                    </Button>
                  </Link>
                </>
              ) : (
                <>
                  <Link href="/register">
                    <Button
                      size="lg"
                      className="w-full sm:w-auto text-lg px-8 py-4"
                    >
                      <UserPlus size={20} />
                      Sign Up Free
                    </Button>
                  </Link>
                  <Link href="/login">
                    <Button
                      variant="outline"
                      size="lg"
                      className="w-full sm:w-auto text-lg px-8 py-4"
                    >
                      <LogIn size={20} />
                      Login
                    </Button>
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-gray-50 dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Why Choose Our Copyright Detection System?
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Empower creators with comprehensive protection against
              unauthorized AI-generated content using their identity, backed by
              cutting-edge technology.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-white dark:bg-gray-900 p-8 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-300"
              >
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 bg-white dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Three-step process to verify content authenticity and detect
              copyright violations in AI-generated media.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-primary-100 dark:bg-primary-900/20 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-primary-600">1</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                Upload Media
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Upload your video or image for analysis. Our system supports
                MP4, AVI, MOV, JPG, and PNG formats.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-primary-100 dark:bg-primary-900/20 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-primary-600">2</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                Dual Analysis
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                First, AI verifies content authenticity. Then, facial embeddings
                are matched against our protected creator database for copyright
                violations.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-primary-100 dark:bg-primary-900/20 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-primary-600">3</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                Get Comprehensive Report
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Receive detailed results showing authenticity status, matched
                identities, confidence scores, and licensing information.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Ready to Protect Creator Rights?
          </h2>
          <p className="text-xl text-primary-100 mb-8">
            Start detecting copyright violations in AI-generated content today.
          </p>
          <Link href="/detect">
            <Button
              size="lg"
              className="bg-white text-primary-600 hover:bg-gray-100 text-lg px-8 py-4"
            >
              Analyze Content
              <ArrowRight size={20} />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
