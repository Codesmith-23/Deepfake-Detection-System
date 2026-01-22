import Link from "next/link";
import { Shield, Eye, Zap, Users, ArrowRight} from "lucide-react";
import Button from "@/components/ui/Button";

export default function Home() {
  const features = [
    {
      icon: <Eye className="h-8 w-8 text-primary-600" />,
      title: "Advanced Detection",
      description:
        "State-of-the-art AI models trained on extensive datasets for accurate deepfake detection.",
    },
    {
      icon: <Zap className="h-8 w-8 text-primary-600" />,
      title: "Fast Processing",
      description:
        "Analyze videos quickly with our optimized processing pipeline and real-time results.",
    },
    {
      icon: <Shield className="h-8 w-8 text-primary-600" />,
      title: "Secure & Private",
      description:
        "Your videos are processed securely and never stored on our servers after analysis.",
    },
    {
      icon: <Users className="h-8 w-8 text-primary-600" />,
      title: "User Friendly",
      description:
        "Simple drag-and-drop interface designed for both technical and non-technical users.",
    },
  ];

  const stats = [
    { label: "Accuracy Rate", value: "95.8%" },
    { label: "Videos Analyzed", value: "50K+" },
    { label: "Response Time", value: "<2min" },
    { label: "Formats Supported", value: "3" },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-primary-50 to-primary-100 dark:from-gray-900 dark:to-gray-800 py-20 sm:py-32">
        <div className="absolute inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] dark:bg-grid-slate-700/25" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold text-gray-900 dark:text-white mb-8">
              Deepfake Detection using
              <br />
              <span className="text-primary-600">DeepCNN</span>
            </h1>

            <p className="text-xl sm:text-2xl text-gray-600 dark:text-gray-300 mb-12 max-w-3xl mx-auto">
              Protect yourself from manipulated media with our cutting-edge deepfake
              detection system powered by advanced deep learning techniques.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
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
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl sm:text-4xl font-bold text-primary-600 mb-2">
                  {stat.value}
                </div>
                <div className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-gray-50 dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Why Choose Our Detection System?
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Built with cutting-edge AI technology and designed for accuracy,
              speed, and ease of use.
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
              Simple three-step process to analyze your videos for deepfake
              content.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-primary-100 dark:bg-primary-900/20 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-primary-600">1</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                Upload Video
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Drag and drop your video file or browse to select. We support
                MP4, AVI, and MOV formats.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-primary-100 dark:bg-primary-900/20 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-primary-600">2</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                AI Analysis
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Our advanced AI models analyze each frame for signs of
                manipulation using deep learning techniques.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-primary-100 dark:bg-primary-900/20 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-primary-600">3</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                Get Results
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Receive detailed results with confidence scores and highlighted
                suspicious frames.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Ready to Detect Deepfakes?
          </h2>
          <p className="text-xl text-primary-100 mb-8">
            Start analyzing your videos today with our free detection service.
          </p>
          <Link href="/detect">
            <Button
              size="lg"
              className="bg-white text-primary-600 hover:bg-gray-100 text-lg px-8 py-4"
            >
              Start Detection
              <ArrowRight size={20} />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
