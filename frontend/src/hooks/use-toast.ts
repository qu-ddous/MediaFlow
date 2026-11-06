"use client";

import { create } from "zustand";
import { ToastMessage, ToastType } from "@/components/ui/toast";

interface ToastStore {
  toasts: ToastMessage[];
  addToast: (toast: Omit<ToastMessage, "id">) => void;
  removeToast: (id: string) => void;
}

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  addToast: (toast) => {
    const id = Math.random().toString(36).substring(2, 9);
    const newToast: ToastMessage = { ...toast, id };

    set((state) => ({
      toasts: [...state.toasts, newToast],
    }));

    // Auto-dismiss after 4 seconds
    setTimeout(() => {
      set((state) => ({
        toasts: state.toasts.filter((t) => t.id !== id),
      }));
    }, 4000);
  },
  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}));

export function useToast() {
  const addToast = useToastStore((s) => s.addToast);
  const removeToast = useToastStore((s) => s.removeToast);
  const toasts = useToastStore((s) => s.toasts);

  const toast = ({
    title,
    description,
    type = "info",
  }: {
    title: string;
    description?: string;
    type?: ToastType;
  }) => {
    addToast({ title, description, type });
  };

  return { toast, toasts, removeToast };
}

