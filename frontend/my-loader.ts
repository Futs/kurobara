export default function customLoader({
  src,
  width,
  quality,
}: {
  src: string
  width: number
  quality?: number
}) {
  // If it's an external URL, return it directly
  if (src.startsWith('http')) {
    return src
  }
  
  // For local images, construct URL to your backend
  return `${process.env.NEXT_PUBLIC_API_URL}/images/${src}?w=${width}&q=${quality || 75}`
}