/* Chaînes d'interface partagées entre les pages FR (racine) et EN (/en/).
   Le contenu long (projets, rendus, mocaplab) reste écrit directement dans
   chaque page — seules les chaînes réutilisées par plusieurs composants
   vivent ici, pour éviter qu'elles divergent entre pages. */
export type Lang = "fr" | "en";

export const UI = {
  fr: {
    nav: { projects: "Projets", renders: "Rendus", mocaplab: "MocapLab", contact: "Contact", cv: "CV" },
    footer: { write: "Écrire —" },
  },
  en: {
    nav: { projects: "Projects", renders: "Renders", mocaplab: "MocapLab", contact: "Contact", cv: "Resume" },
    footer: { write: "Write —" },
  },
} as const;

/* Chemin équivalent dans l'autre langue : les routes FR/EN sont un miroir
   exact (même slugs), donc un simple ajout/retrait du préfixe /en suffit. */
export function otherLangPath(pathname: string, lang: Lang): string {
  if (lang === "fr") {
    return "/en" + pathname;
  }
  const stripped = pathname.replace(/^\/en/, "");
  return stripped === "" ? "/" : stripped;
}
