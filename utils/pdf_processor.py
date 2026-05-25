"""
Module de traitement des documents PDF
Extraction, nettoyage et découpage du texte
"""

import PyPDF2
import pdfplumber
import re
from typing import List, Dict

class PDFProcessor:
    def __init__(self):
        self.max_chunk_size = 1000  # Taille maximale des segments
        self.overlap = 200  # Chevauchement entre segments
        
    def extract_text(self, pdf_path: str) -> str:
        """
        Extrait le texte d'un fichier PDF en utilisant pdfplumber (plus précis)
        """
        text = ""
        
        try:
            # Utilisation de pdfplumber pour une meilleure précision
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num} ---\n"
                        text += page_text
                    
        except Exception as e:
            # Fallback avec PyPDF2 si pdfplumber échoue
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        text += f"\n--- Page {page_num} ---\n"
                        text += page.extract_text()
            except Exception as e2:
                raise Exception(f"Erreur extraction PDF: {str(e2)}")
        
        # Nettoyage du texte
        text = self._clean_text(text)
        
        if not text.strip():
            raise Exception("Aucun texte n'a pu être extrait du PDF")
        
        return text
    
    def _clean_text(self, text: str) -> str:
        """
        Nettoie le texte extrait
        """
        # Supprimer les caractères spéciaux inutiles
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\.\,\?\:\;\!\-\'\"\(\)\n]', '', text)
        # Supprimer les espaces multiples
        text = re.sub(r' +', ' ', text)
        # Normaliser les sauts de ligne
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def chunk_text(self, text: str) -> List[Dict[str, str]]:
        """
        Découpe le texte en segments (chunks) pour le traitement
        """
        chunks = []
        
        # Sépare par paragraphes et pages
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        current_page = 1
        
        for para in paragraphs:
            # Détection du numéro de page
            page_match = re.search(r'--- Page (\d+) ---', para)
            if page_match:
                current_page = int(page_match.group(1))
                continue
            
            # Si l'ajout dépasse la taille max, sauvegarder le chunk actuel
            if len(current_chunk) + len(para) > self.max_chunk_size:
                if current_chunk:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "page": current_page,
                        "metadata": {
                            "length": len(current_chunk),
                            "timestamp": str(datetime.now())
                        }
                    })
                
                # Nouveau chunk avec chevauchement
                current_chunk = current_chunk[-self.overlap:] if current_chunk else ""
                current_chunk += "\n" + para
            else:
                current_chunk += "\n" + para if current_chunk else para
        
        # Dernier chunk
        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "page": current_page,
                "metadata": {
                    "length": len(current_chunk),
                    "timestamp": str(datetime.now())
                }
            })
        
        return chunks

# Pour éviter l'erreur datetime
from datetime import datetime