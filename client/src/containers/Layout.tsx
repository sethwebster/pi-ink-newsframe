import React from "react";

export default function Layout({ children }: { children: JSX.Element }) {
  return <div className="flex flex-grow bg-blue-600 w-screen h-full">{children}</div>;
}
