"""Dealer data extraction logic"""

from typing import List
import logging
import re
from ..models.dealer import DealerData
from ..exceptions import ParseException


class DealerExtractor:
    """Extracts dealer data from pages"""
    
    def __init__(self):
        self.logger = logging.getLogger('DealerExtractor')
    
    async def extract_dealers(
        self, 
        page, 
        vehicle_type: str, 
        brand: str, 
        location: str,
        source_url: str
    ) -> List[DealerData]:
        """Extract dealer data from ZigWheels showroom pages"""
        dealers = []
        
        try:
            # Wait for page content to load
            await page.wait_for_timeout(2000)
            
            # Extract dealer blocks from page using specific HTML structure
            raw_dealers = await page.evaluate(r"""() => {
                const results = [];
                const seenNames = new Set();
                
                // Target the dealer card structure - look for divs with class containing 'deal-crd'
                const dealerCards = document.querySelectorAll('[class*="deal-crd"]');
                
                if (dealerCards.length > 0) {
                    dealerCards.forEach(card => {
                        try {
                            // Extract dealer name from h3
                            const nameElem = card.querySelector('h3');
                            const dealerName = nameElem ? nameElem.innerText.trim() : '';
                            
                            if (!dealerName || dealerName.length < 2) return;
                            
                            // Extract address - look for paragraphs within the card
                            let address = '';
                            const paragraphs = card.querySelectorAll('p');
                            if (paragraphs.length > 0) {
                                // First paragraph is usually the address
                                address = paragraphs[0].innerText.trim();
                            }
                            
                            // Extract email - look for email pattern in card text
                            let email = '';
                            const cardText = card.innerText || card.textContent || '';
                            const emailMatch = cardText.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
                            if (emailMatch) {
                                email = emailMatch[0];
                            }
                            
                            // Extract phone - look for tel links
                            let phone = '';
                            const telLink = card.querySelector('a[href^="tel:"]');
                            if (telLink) {
                                phone = telLink.innerText.trim();
                            } else {
                                // Fallback: look for phone pattern in text (10+ digits)
                                const phoneMatch = cardText.match(/[0-9]{10,}/);
                                if (phoneMatch) {
                                    phone = phoneMatch[0];
                                }
                            }
                            
                            const key = dealerName.toLowerCase().trim();
                            if (!seenNames.has(key) && dealerName.length > 3) {
                                results.push({
                                    dealer_name: dealerName,
                                    address: address,
                                    email: email,
                                    phone: phone
                                });
                                seenNames.add(key);
                            }
                        } catch (e) {
                            console.debug('Error processing card:', e);
                        }
                    });
                }
                
                return results;
            }""")
            
            self.logger.debug(f"Found {len(raw_dealers)} dealer blocks on page")
            
            for raw in raw_dealers:
                if not raw or not raw.get('dealer_name'):
                    continue
                
                # Extract city and state from address
                city, state, pincode = self._parse_location(raw.get('address', ''))
                
                try:
                    dealer = DealerData(
                        vehicle_type=vehicle_type,
                        brand=brand,
                        location=location,
                        dealer_name=self._clean_name(raw.get('dealer_name', '')),
                        address=raw.get('address', ''),
                        phone=self._clean_phone(raw.get('phone', '')),
                        email=self._clean_email(raw.get('email', '')),
                        city=city,
                        state=state,
                        pincode=pincode,
                        source_url=source_url
                    )
                    dealers.append(dealer)
                except Exception as e:
                    self.logger.debug(f"Error creating DealerData: {str(e)}")
                    continue
            
            self.logger.debug(f"Extracted {len(dealers)} valid dealers from {source_url}")
            return dealers
        
        except Exception as e:
            self.logger.error(f"Error extracting dealers: {str(e)}")
            return []
    
    def _clean_name(self, name: str) -> str:
        """Clean dealer name"""
        return name.strip().split('\n')[0] if name else ''
    
    def _clean_phone(self, phone: str) -> str:
        """Extract and clean phone number"""
        if not phone:
            return ''
        # Keep only digits, +, and -
        cleaned = re.sub(r'[^\d+\-]', '', phone)
        return cleaned
    
    def _clean_email(self, email: str) -> str:
        """Extract and clean email"""
        if not email:
            return ''
        email = email.strip()
        # Validate email format
        if '@' in email and '.' in email.split('@')[-1]:
            return email
        return ''
    
    def _parse_location(self, address: str) -> tuple:
        """Parse city, state, pincode from address"""
        if not address:
            return '', '', ''
        
        city = ''
        state = ''
        pincode = ''
        
        # Extract pincode (6 consecutive digits)
        pincode_match = re.search(r'\b(\d{6})\b', address)
        if pincode_match:
            pincode = pincode_match.group(1)
        
        # Extract state (comprehensive list of Indian states)
        states = [
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
            'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
            'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
            'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
            'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
            'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Delhi', 'Jammu and Kashmir',
            'Ladakh', 'Puducherry'
        ]
        for s in states:
            if s in address:
                state = s
                break
        
        # Extract city (comprehensive list of major Indian cities)
        cities = [
            'Hyderabad', 'Bangalore', 'Mumbai', 'Delhi', 'Chennai', 'Pune', 'Ahmedabad',
            'Jaipur', 'Lucknow', 'Indore', 'Chandigarh', 'Kochi', 'Kolkata', 'Surat',
            'Nagpur', 'Vadodara', 'Goa', 'Agra', 'Visakhapatnam', 'Patna', 'Bhopal',
            'Ludhiana', 'Kanpur', 'Srinagar', 'Varanasi', 'Meerut', 'Amritsar', 'Guwahati',
            'Jamshedpur', 'Noida', 'Gurgaon', 'Faridabad', 'Thane', 'Aurangabad', 'Ranchi',
            'Ghaziabad', 'Coimbatore', 'Mysore', 'Trivandrum', 'Kota', 'Udaipur'
        ]
        for c in cities:
            if c in address:
                city = c
                break
        
        return city, state, pincode
