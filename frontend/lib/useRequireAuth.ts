"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { getToken } from "./auth";

type AuthState = "checking" | "authed" | "unauthed";

export function useRequireAuth(): boolean {
  const router = useRouter();
  const [state, setState] = useState<AuthState>("checking");

  // The token only exists in the browser, so this can only be checked after
  // mount. Rendering "checking" (-> null) on both the server and the first
  // client pass keeps hydration consistent; only this post-mount effect
  // reads localStorage and decides whether to redirect.
  useEffect(() => {
    if (getToken()) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setState("authed");
    } else {
      setState("unauthed");
      router.replace("/login");
    }
  }, [router]);

  return state === "authed";
}
