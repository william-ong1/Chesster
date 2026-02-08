import { createBrowserRouter } from "react-router";
import { OnboardingLayout } from "./components/OnboardingLayout";
import { Welcome } from "./components/onboarding/Welcome";
import { ImportGames } from "./components/onboarding/ImportGames";
import { Analyzing } from "./components/onboarding/Analyzing";
import { StyleProfile } from "./components/onboarding/StyleProfile";
import { BotSettings } from "./components/onboarding/BotSettings";
import { Training } from "./components/onboarding/Training";
import { Complete } from "./components/onboarding/Complete";
import { Dashboard } from "./components/Dashboard";
import { ChessGame } from "./components/ChessGame";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: OnboardingLayout,
    children: [
      { index: true, Component: Welcome },
      { path: "import", Component: ImportGames },
      { path: "analyzing", Component: Analyzing },
      { path: "profile", Component: StyleProfile },
      { path: "settings", Component: BotSettings },
      { path: "training", Component: Training },
      { path: "complete", Component: Complete },
      { path: "dashboard", Component: Dashboard },
      { path: "play", Component: ChessGame },
    ],
  },
]);