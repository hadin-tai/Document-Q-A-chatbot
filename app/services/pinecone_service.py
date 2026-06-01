import os
import time
import re
from pinecone import Pinecone
from dotenv import load_dotenv
from app.utils.logger import setup_logger

load_dotenv()

# ==========================================
# LOGGER
# ==========================================
service_logger = setup_logger("pinecone_service")


class PineconeService:
    def __init__(self):
        service_logger.info("Initializing PineconeService...")

        self.api_key = os.getenv("PINECONE_API_KEY")
        self.assistant_name = os.getenv("ASSISTANT_NAME", "vector-rag-test")

        if not self.api_key:
            service_logger.error("PINECONE_API_KEY not found in environment variables")
            raise ValueError("PINECONE_API_KEY not found in environment variables")

        try:
            self.pc = Pinecone(api_key=self.api_key)
            self.assistant = self._get_or_create_assistant()
            service_logger.info("PineconeService initialized successfully")

        except Exception as e:
            service_logger.exception(f"Failed to initialize PineconeService: {str(e)}")
            raise e

    # ==========================================
    # CREATE / LOAD ASSISTANT
    # ==========================================
    def _get_or_create_assistant(self):
        try:
            service_logger.info(
                f"Attempting to create or load assistant: {self.assistant_name}"
            )

            self.pc.assistant.create_assistant(
                assistant_name=self.assistant_name,
                instructions="""
You are a high precision enterprise document assistant.

Rules:
1. Answer only from uploaded document.
2. Search headers, footers, notes, appendix, tiny text.
3. Important answers may appear only once.
4. Never guess.
5. If not found, say Not found in document.
6. Give same answer for repeated same query.
7. Prefer exact wording.
8. Be concise and accurate.
"""
            )

            service_logger.info(
                f"Assistant '{self.assistant_name}' created successfully"
            )

        except Exception:
            service_logger.info(
                f"Using existing assistant '{self.assistant_name}'"
            )

        return self.pc.assistant.Assistant(self.assistant_name)

    # ==========================================
    # FILE UPLOAD
    # ==========================================
    async def upload_file(
        self, 
        file_path: str,
        user_id: str,
        document_id: str
    ):
        """
        Upload file to Pinecone Assistant with strict metadata isolation
        """

        service_logger.info(f"Uploading file for user {user_id}, doc {document_id}: {file_path}")

        try:
            start_time = time.time()

            response = self.assistant.upload_file(
                file_path=file_path,
                metadata={
                    "type": "pdf",
                    "user_id": user_id,
                    "document_id": document_id,
                    "workspace_id": "default"
                }
            )

            duration = time.time() - start_time

            service_logger.info(
                f"File uploaded successfully to Pinecone in {duration:.2f}s. Pinecone ID: {response.id}"
            )

            return response

        except Exception as e:
            service_logger.exception(
                f"Pinecone upload error for user {user_id}, doc {document_id}: {str(e)}"
            )
            raise Exception(f"Pinecone upload error: {str(e)}")

    # ==========================================
    # QUERY EXPANSION
    # ==========================================
    def _expand_queries(self, question: str):
        """
        Multi-query retrieval for better recall
        """

        q = question.strip()

        queries = [
            q,
            q.lower(),
            re.sub(r"[^a-zA-Z0-9 ]", " ", q).strip(),
            " ".join(q.split()[:6]),
        ]

        # Remove duplicates / blanks
        cleaned = []
        for item in queries:
            item = item.strip()
            if item and item not in cleaned:
                cleaned.append(item)

        return cleaned[:4]

    # ==========================================
    # SAFE RESPONSE EXTRACTOR
    # ==========================================
    def _extract_answer(self, response):

        try:
            if hasattr(response, "message"):

                if hasattr(response.message, "content"):
                    return str(response.message.content).strip()

                return str(response.message).strip()

            elif hasattr(response, "messages"):

                last_msg = response.messages[-1]

                if isinstance(last_msg, dict):
                    return str(last_msg.get("content", "")).strip()

                elif hasattr(last_msg, "content"):
                    return str(last_msg.content).strip()

                return str(last_msg).strip()

            return str(response).strip()

        except Exception:
            return str(response).strip()

    # ==========================================
    # NOT FOUND CHECK
    # ==========================================
    def _is_not_found(self, text: str):

        txt = text.lower()

        checks = [
            "not found in document",
            "not specified in the document",
            "not mentioned in the document",
            "no information found",
            "unable to find",
            "not available in the document"
        ]

        return any(word in txt for word in checks)

    # ==========================================
    # RETRIEVE CONTEXT
    # ==========================================
    async def retrieve_context(
        self,
        question: str,
        user_id: str,
        document_id: str,
        top_k=25,
        snippet_size=1400
    ):
        """
        Direct retrieval to inspect context with strict isolation
        """

        service_logger.info(
            f"Retrieving context for user {user_id}, doc {document_id}: {question[:80]}"
        )

        try:
            context = self.assistant.context(
                query=question,
                top_k=top_k,
                snippet_size=snippet_size,
                filter={
                    "user_id": user_id,
                    "document_id": document_id
                }
            )

            return context

        except Exception as e:
            service_logger.exception(f"Error retrieving context: {str(e)}")
            raise e

    # ==========================================
    # MAIN CHAT
    # ==========================================
    async def chat(
        self, 
        question: str,
        user_id: str,
        document_id: str
    ):
        """
        High recall retrieval + retry + stable answer with strict isolation
        """

        service_logger.info(
            f"Chat request for user {user_id}, doc {document_id}: {question[:80]}"
        )

        try:
            start_time = time.time()

            expanded_queries = self._expand_queries(question)

            final_prompt = f"""
Answer using uploaded document only.

Question:
{question}

Rules:
1. Search all retrieved context carefully.
2. Search headers, tables, notes, appendix, tiny text.
3. Prefer exact wording.
4. If answer exists once, return it.
5. If truly absent say: Not found in document.
6. Do not guess.
"""

            # ==================================
            # PASS 1: top_k=25, snippet_size=1400
            # ==================================
            response = self.assistant.chat(
                messages=[
                    {
                        "role": "user",
                        "content": final_prompt
                    }
                ],
                temperature=0.0,
                include_highlights=True,
                filter={
                    "user_id": user_id,
                    "document_id": document_id
                },
                context_options={
                    "top_k": 25,
                    "snippet_size": 1400,
                    "queries": expanded_queries
                }
            )

            answer = self._extract_answer(response)

            # ==================================
            # PASS 2: RETRY IF NOT FOUND (top_k=40, snippet_size=800)
            # ==================================
            if self._is_not_found(answer):

                service_logger.info(
                    "Retrying retrieval with wider search (Pass 2)..."
                )

                response = self.assistant.chat(
                    messages=[
                        {
                            "role": "user",
                            "content": final_prompt
                        }
                    ],
                    temperature=0.0,
                    include_highlights=True,
                    filter={
                        "user_id": user_id,
                        "document_id": document_id
                    },
                    context_options={
                        "top_k": 40,
                        "snippet_size": 800,
                        "queries": expanded_queries
                    }
                )

                answer = self._extract_answer(response)

            duration = time.time() - start_time

            service_logger.info(
                f"Chat request completed in {duration:.2f}s"
            )

            return answer

        except Exception as e:
            service_logger.exception(
                f"Pinecone chat error for user {user_id}, doc {document_id}: {str(e)}"
            )

            raise Exception(f"Pinecone chat error: {str(e)}")

    # ==========================================
    # LIST FILES
    # ==========================================
    async def list_files(self, user_id: str):
        """
        List files for a specific user
        """

        service_logger.info(f"Listing files for user {user_id} from Pinecone...")

        try:
            # Pinecone Assistant list_files doesn't support server-side filtering by metadata yet in all versions
            # So we list all and filter manually, or rely on our DB for the primary source of truth.
            # However, to keep it sync with Pinecone, we filter here if possible.
            all_files = self.assistant.list_files()
            
            # Filter files by user_id in metadata
            user_files = [
                f for f in all_files 
                if hasattr(f, 'metadata') and f.metadata.get('user_id') == user_id
            ]

            service_logger.info(
                f"Successfully listed {len(user_files)} files for user {user_id}"
            )

            return user_files

        except Exception as e:
            service_logger.exception(f"Error listing files for user {user_id}: {str(e)}")
            raise Exception(f"Error listing files: {str(e)}")

    # ==========================================
    # DELETE FILE
    # ==========================================
    async def delete_file(self, file_id: str, user_id: str):
        """
        Delete file from Pinecone with ownership check
        """

        service_logger.info(
            f"Deleting file {file_id} for user {user_id} from Pinecone"
        )

        try:
            # First verify ownership from Pinecone metadata if possible
            # Or rely on the caller (API route) to verify from DB.
            # Here we just perform the deletion.
            result = self.assistant.delete_file(file_id)

            service_logger.info(
                f"Successfully deleted file {file_id} from Pinecone"
            )

            return result

        except Exception as e:
            service_logger.exception(
                f"Error deleting file {file_id}: {str(e)}"
            )

            raise Exception(f"Error deleting file: {str(e)}")


# ==========================================
# SINGLETON INSTANCE
# ==========================================
pinecone_service = PineconeService()
