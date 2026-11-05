import React from "react";
import Image from "next/image";
import { Clock, Globe, Film, Music, CheckCircle } from "lucide-react";
import { MediaInfo } from "@/types";
import { formatDuration } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

interface MediaPreviewProps {
  media: MediaInfo;
}

export function MediaPreview({ media }: MediaPreviewProps) {
  const isVideo = media.media_type === "video";

  return (
    <div className="flex flex-col sm:flex-row items-center gap-5 p-5 rounded-2xl bg-white border border-slate-200/90 shadow-sm">
      {/* Thumbnail */}
      <div className="relative w-full sm:w-56 aspect-video rounded-xl overflow-hidden bg-slate-100 flex-shrink-0 flex items-center justify-center">
        {media.thumbnail_url ? (
          <img
            src={media.thumbnail_url}
            alt={media.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="flex flex-col items-center justify-center text-slate-400 gap-1.5">
            {isVideo ? <Film className="h-8 w-8" /> : <Music className="h-8 w-8" />}
            <span className="text-[11px] font-medium">No preview available</span>
          </div>
        )}

        {media.duration && (
          <div className="absolute bottom-2 right-2 bg-black/75 backdrop-blur-sm text-white px-2 py-0.5 rounded text-[11px] font-medium flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {media.duration_string || formatDuration(media.duration)}
          </div>
        )}
      </div>

      {/* Info */}
      <div className="flex-1 w-full space-y-2.5">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="default" className="capitalize">
            <Globe className="h-3 w-3 mr-1" />
            {media.source_name || "Direct File"}
          </Badge>
          <Badge variant="neutral">
            {isVideo ? "Video Stream" : "Audio Track"}
          </Badge>
          {media.original_format && (
            <Badge variant="neutral" className="uppercase">
              .{media.original_format}
            </Badge>
          )}
        </div>

        <h3 className="text-base sm:text-lg font-bold text-slate-900 leading-snug line-clamp-2">
          {media.title || "Untitled Media"}
        </h3>

        <p className="text-xs text-slate-500 break-all line-clamp-1">
          {media.url}
        </p>
      </div>
    </div>
  );
}

