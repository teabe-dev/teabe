
def tuple_list_to_dict(tuple_list) -> dict:
    # [(1, '薇霜'), (3, '比比')] > {1: '薇霜', 3: '比比' }
    return {t[0]: t[1] for t in tuple_list}


def get_dict_value(key, dictionary:dict) -> any:
    print(key, dictionary)
    return dictionary.get(key, str(key))


def calculate_debts(amounts:dict) -> list:
    # 計算 誰要給誰多少錢 演算法
    # {1: -92912819, 3: 148785942, 7: -4476621, 8: 23067896, 9: -74464398}
    # ︾ ︾ ︾ ︾
    # [(1, 3, 92912819), (7, 3, 4476621), (9, 3, 51396502), (9, 8, 23067896)]
    lenders = {person: amount for person, amount in amounts.items() if amount > 0}
    borrowers = {person: -amount for person, amount in amounts.items() if amount < 0}
    transactions = []
    for lender_key in list(lenders.keys()):
        for borrower_key in list(borrowers.keys()):
            if lenders[lender_key] > borrowers[borrower_key]:
                transactions.append((borrower_key, lender_key, borrowers[borrower_key]))
                lenders[lender_key] -= borrowers[borrower_key]
                del borrowers[borrower_key]
            else:
                transactions.append((borrower_key, lender_key, lenders[lender_key]))
                borrowers[borrower_key] -= lenders[lender_key]
                del lenders[lender_key]
                break
    return transactions