import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # List of probabilities that every event specified happens for each person

    probabilities = {}
    currentPersonGeneProb = 0.0
    currentPersonTraitProb = 0.0
    oddsMotherPass = 0.0
    oddsMotherNoPass = 0.0
    oddsFatherPass = 0.0
    oddsFatherNoPass = 0.0

    
    for person in people:
        # GENE SECTION
        # First, see if the person has specified parents
        if people[person]["mother"] != None:
            # First calculate each probabilities weither his parents has one tow or none gene(s)
            if people[person]["mother"] in one_gene:
                oddsMotherPass = 0.5 + PROBS["mutation"]
                oddsMotherNoPass = 0.5 - PROBS["mutation"]
            elif people[person]["mother"] in two_genes:
                oddsMotherPass = 1.0 - PROBS["mutation"]
                oddsMotherNoPass = PROBS["mutation"]
            else:
                # The mother has no gene
                oddsMotherPass = PROBS["mutation"]
                oddsMotherNoPass = 1 - PROBS["mutation"]
            if people[person]["father"] in one_gene:
                oddsFatherPass = 0.5 + PROBS["mutation"]
                oddsFatherNoPass = 0.5 - PROBS["mutation"]
            elif people[person]["father"] in two_genes:
                    oddsFatherPass = 1.0 - PROBS["mutation"]
                    oddsFatherNoPass = PROBS["mutation"]
            else:
                # The father has no gene
                oddsFatherPass = PROBS["mutation"]
                oddsFatherNoPass = 1.0 - PROBS["mutation"]
            if person in one_gene:
                # Calulate the prob that this person has one gene depending of its parent's genes
                # This person will either receive one gene from his father and (*) zero from his mother
                # Or (+) vice-versa
                currentPersonGeneProb = oddsFatherPass*oddsMotherNoPass + oddsFatherNoPass*oddsMotherPass
                print(currentPersonGeneProb)
                if person in have_trait:
                    currentPersonTraitProb = PROBS["trait"][1][True]
                else:
                    currentPersonTraitProb = PROBS["trait"][1][False]
                    print(currentPersonTraitProb)
            elif person in two_genes:
                currentPersonGeneProb = oddsFatherPass*oddsMotherPass
                if person in have_trait:
                    currentPersonTraitProb = PROBS["trait"][2][True]
                else:
                    currentPersonTraitProb = PROBS["trait"][2][False]
            else:
                # Current person has parents and no genes
                currentPersonGeneProb = oddsFatherNoPass*oddsMotherNoPass
                if person in have_trait:
                    currentPersonTraitProb = PROBS["trait"][0][True]
                else:
                    currentPersonTraitProb = PROBS["trait"][0][False]

        else:
            # No parents, we will assign the unconditional prob
            if person in one_gene:
                currentPersonGeneProb = PROBS["gene"][1]
                if person in have_trait:
                    currentPersonTraitProb = PROBS["trait"][1][True]
                else:
                    currentPersonTraitProb = PROBS["trait"][1][False]
            elif person in two_genes:
                currentPersonGeneProb = PROBS["gene"][2]
                if person in have_trait:
                    currentPersonTraitProb = PROBS["trait"][2][True]
                else:
                    currentPersonTraitProb = PROBS["trait"][2][False]
            else:
                # The current person has no gene
                currentPersonGeneProb = PROBS["gene"][0]
                if person in have_trait:
                    currentPersonTraitProb = PROBS["trait"][0][True]
                else:
                    currentPersonTraitProb = PROBS["trait"][0][False]

        # We add the current prob to the prob dict
        probabilities[person] = currentPersonTraitProb * currentPersonGeneProb
    print(probabilities)
    # Calculate p
    i = 0
    
    p = list(probabilities.values())[0]
    for prob in probabilities:
        if i == 0:
            i += 1
            continue
        p *= probabilities[prob]
    print(p)
    return p
        
def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    totalGene = 0
    totalTrait = 0
    print(probabilities)
    for person in probabilities:
        totalGene = 0
        totalTrait = 0
        for gene, prob in probabilities[person]["gene"].items():
            totalGene += prob
        for gene, prob in probabilities[person]["gene"].items():
            probabilities[person]["gene"][gene] = prob/totalGene
        for trait, prob in probabilities[person]["trait"].items():
            totalTrait += prob
            # print(prob)
        for trait, prob in probabilities[person]["trait"].items():
            probabilities[person]["trait"][trait] = prob/totalTrait


if __name__ == "__main__":
    main()
