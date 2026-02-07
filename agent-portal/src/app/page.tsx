import { redirect } from "next/navigation";

export default function Home() {
  // Check auth here later
  redirect("/login");
}
