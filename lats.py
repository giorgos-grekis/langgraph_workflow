from typing import TypedDict, Annotated, List
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

_ = load_dotenv()


# 1. Ορίζουμε τη δομή για την απάντηση του Κριτή (Reflect)
class Evaluation(BaseModel):
    score: int = Field(description="Βαθμολογία από το 1 έως το 10.")
    feedback: str = Field(description="Τι λείπει ή τι πρέπει να διορθωθεί. Αν είναι τέλειο, γράψε 'Κανένα σχόλιο'.")
    is_approved: bool = Field(description="True αν το score είναι >= 8, αλλιώς False.")


# 2. Το State του Agent
class State(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    draft: str  # Εδώ αποθηκεύουμε το τρέχον κείμενο
    iterations: int  # Για να μην πέσουμε σε άπειρη λούπα
    best_draft: str   # ΠΡΟΣΘΗΚΗ: Το καλύτερο κείμενο μέχρι στιγμής
    best_score: int   # ΠΡΟΣΘΗΚΗ: Το υψηλότερο σκορ που έχουμε πάρει


model = ChatOpenAI(model="gpt-4.1-nano")


# ==========================================
# GENERATE (Παραγωγή / Διόρθωση)
# ==========================================
def generate_node(state: State):
    print("--- ΚΑΛΕΣΜΑ GENERATE ---")

    # Το σύστημα ξέρει αν γράφει για πρώτη φορά ή αν διορθώνει βάσει του feedback
    sys_msg = SystemMessage(content="Είσαι ένας εξαιρετικός copywriter. Γράψε αυτό που σου ζητάει ο χρήστης.")

    messages = [sys_msg] + state["messages"]
    response = model.invoke(messages)

    # Προσθέτουμε την απάντηση στο ιστορικό και αυξάνουμε τα iterations
    new_iterations = state.get("iterations", 0) + 1

    return {
        "messages": [response],
        "draft": response.content,
        "iterations": new_iterations
    }


# ==========================================
# REFLECT (Αξιολόγηση / Κριτική)
# ==========================================
def reflect_node(state: State):
    print("--- ΚΑΛΕΣΜΑ REFLECT (ΚΡΙΤΗΣ) ---")

    evaluator_model = model.with_structured_output(Evaluation)
    prompt = f"Αξιολόγησε το παρακάτω κείμενο...\nΚείμενο: {state['draft']}"
    evaluation = evaluator_model.invoke([HumanMessage(content=prompt)])

    print(f"Σκορ: {evaluation.score}/10 | Εγκρίθηκε: {evaluation.is_approved}")
    print(f"Feedback: {evaluation.feedback}\n")

    # === ΝΕΑ ΛΟΓΙΚΗ ΑΠΟΘΗΚΕΥΣΗΣ ΤΟΥ ΚΑΛΥΤΕΡΟΥ ===
    current_best_score = state.get("best_score", 0)
    updates = {}

    if evaluation.score > current_best_score:
        updates["best_score"] = evaluation.score
        updates["best_draft"] = state["draft"]
        print(f"🏆 Νέο καλύτερο σκορ! ({evaluation.score}/10) Αποθηκεύτηκε.\n")
    # ============================================

    if not evaluation.is_approved:
        feedback_msg = HumanMessage(
            content=f"Ο κριτής απέρριψε το κείμενο. Feedback: {evaluation.feedback}. Ξαναγράψτο.")
        updates["messages"] = [feedback_msg]
        return updates

    return updates


# ==========================================
# ΣΥΝΘΗΚΗ: Πάμε στο τέλος ή πίσω στο Generate;
# ==========================================
def route_after_reflection(state: State):
    # Ελέγχουμε το τελευταίο μήνυμα
    last_message = state["messages"][-1]

    # Αν έχουμε κολλήσει σε λούπα, το κόβουμε
    if state["iterations"] >= 3:
        print("--- ΤΕΛΟΣ ΛΟΓΩ ΟΡΙΟΥ ΠΡΟΣΠΑΘΕΙΩΝ ---")
        return END

    # Αν το τελευταίο μήνυμα είναι από τον χρήστη (δηλαδή το feedback του κριτή), πάμε ξανά στο Generate
    if isinstance(last_message, HumanMessage):
        print("--- ΠΙΣΩ ΣΤΟ GENERATE ΓΙΑ ΔΙΟΡΘΩΣΗ ---")
        return "generate"

    # Αλλιώς, τελειώσαμε επιτυχώς!
    print("--- ΤΕΛΟΣ ΜΕ ΕΠΙΤΥΧΙΑ ---")
    return END


# ==========================================
# ΣΤΗΣΙΜΟ ΓΡΑΦΗΜΑΤΟΣ
# ==========================================
workflow = StateGraph(State)
workflow.add_node("generate", generate_node)
workflow.add_node("reflect", reflect_node)

workflow.set_entry_point("generate")
workflow.add_edge("generate", "reflect")
workflow.add_conditional_edges("reflect", route_after_reflection)

app = workflow.compile()

if __name__ == "__main__":
    # 1. Φτιάχνουμε το αρχικό State δίνοντας το πρόβλημα στον Agent
    initial_input = {
        "messages": [HumanMessage(content="Γράψε ένα πολύ σύντομο και πιασάρικο σλόγκαν...")],
        "iterations": 0,
        "draft": "",
        "best_draft": "",
        "best_score": 0
    }

    print(" Ξεκινάει το LATS Workflow (Generate -> Reflect)...\n")

    # 2. Τρέχουμε το γράφημα με τη μέθοδο invoke()
    # Επειδή έχουμε βάλει print() μέσα στους κόμβους, θα βλέπεις ζωντανά τη "σκέψη" του!
    final_state = app.invoke(initial_input)
    print("\n===========================================")
    print("ΙΣΤΟΡΙΚΟ ΠΡΟΣΠΑΘΕΙΩΝ ΚΑΙ ΑΠΟΡΡΙΨΕΩΝ")
    print("===========================================\n")

    # Διατρέχουμε όλα τα μηνύματα στο ιστορικό
    for i, msg in enumerate(final_state["messages"]):
        if msg.type == "ai":
            print(f"🤖 ΠΡΟΣΠΑΘΕΙΑ: {msg.content}")
        elif msg.type == "human" and "Ο κριτής απέρριψε" in msg.content:
            print(f"❌ ΚΡΙΤΙΚΗ: {msg.content}\n")
            print("-" * 40)

    # 3. Τυπώνουμε το τελικό, εγκεκριμένο αποτέλεσμα
    print("\n✨ ΤΟ ΚΑΛΥΤΕΡΟ ΑΠΟΤΕΛΕΣΜΑ ΠΟΥ ΒΡΕΘΗΚΕ ✨")
    print(f"Σκορ: {final_state.get('best_score')}/10")
    print(final_state.get("best_draft"))

